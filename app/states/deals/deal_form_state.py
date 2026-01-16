import reflex as rx
import logging
from enum import Enum
from datetime import datetime
from pydantic import ValidationError
from app.states.shared.schema import Deal


class FormMode(str, Enum):
    ADD = "add"
    EDIT = "edit"
    REVIEW = "review"


class DealFormState(rx.State):
    form_mode: FormMode = FormMode.ADD
    form_values: dict[str, str | int | float | bool | None] = {}
    validation_results: dict[str, dict[str, str | bool | None]] = {}
    is_dirty: bool = False
    is_submitting: bool = False
    touched_fields: list[str] = []
    form_key: int = 0  # Increment to force form remount

    @rx.var
    def has_errors(self) -> bool:
        return any(
            (not r.get("is_valid", True) for r in self.validation_results.values())
        )

    @rx.var
    def error_count(self) -> int:
        return sum(
            (1 for r in self.validation_results.values() if not r.get("is_valid", True))
        )

    @rx.var
    def field_errors(self) -> dict[str, str]:
        """Returns a dictionary of field_name -> error_message for invalid fields."""
        errors = {}
        for field, result in self.validation_results.items():
            if not result.get("is_valid", True) and result.get("error_message"):
                errors[field] = result["error_message"]
        return errors

    @rx.var
    def can_submit(self) -> bool:
        is_valid = not self.has_errors
        has_required = bool(
            self.form_values.get("ticker") and self.form_values.get("structure")
        )
        return is_valid and (not self.is_submitting) and has_required

    @rx.event
    def set_field_value(self, field: str, value: str | int | float | bool | None):
        self.form_values[field] = value
        self.is_dirty = True
        self._validate_single_field(field)
        cross_triggers = {
            "flag_bought": ["offering_price"],
            "warrants_min": ["warrants_strike", "warrants_exp"],
            "primary_shares": ["shares_amount"],
            "secondary_shares": ["shares_amount"],
            "shares_amount": ["primary_shares", "secondary_shares"],
            "announce_date": ["pricing_date"],
        }
        if field in cross_triggers:
            for related in cross_triggers[field]:
                self._validate_single_field(related)

    @rx.event
    def touch_field(self, field: str):
        if field not in self.touched_fields:
            self.touched_fields.append(field)
            self._validate_single_field(field)

    def _validate_single_field(self, field: str):
        self.validate_form()

    @rx.event
    def validate_form(self):
        results = {}
        if not self.form_values.get("ticker") or not self.form_values.get("structure"):
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
            self.validation_results = results
            return
        try:
            data = {}
            for k, v in self.form_values.items():
                if v == "" and k not in [
                    "ticker",
                    "structure",
                    "created_at",
                    "updated_at",
                ]:
                    data[k] = None
                else:
                    data[k] = v
            Deal(**{**{"created_at": "", "updated_at": ""}, **data})
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
        except ValidationError as e:
            logging.exception(f"Validation error details: {e}")
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
            for error in e.errors():
                field_name = error["loc"][0]
                msg = error["msg"]
                if msg.startswith("Value error, "):
                    msg = msg.replace("Value error, ", "")
                results[str(field_name)] = {"is_valid": False, "error_message": msg}
        self.validation_results = results
        if not self.touched_fields:
            self.touched_fields = list(self.form_values.keys())

    @rx.event
    def reset_form(self):
        self.form_values = {}
        self.validation_results = {}
        self.touched_fields = []
        self.is_dirty = False
        self.is_submitting = False
        self.form_mode = FormMode.ADD
        self.form_key += 1  # Force form remount

    @rx.event
    def on_page_load(self):
        """Handle add page load - check query params to determine mode.

        If mode=edit is in URL, preserve form data for editing.
        Otherwise, reset form for a fresh add.
        """
        mode = self.router.page.params.get("mode", "add")
        if mode != "edit":
            self.reset_form()

    @rx.event
    def load_deal_for_edit(self, deal: Deal, mode: str = "edit"):
        self.reset_form()
        processed_values = deal.dict()
        for k, v in processed_values.items():
            if isinstance(v, datetime):
                processed_values[k] = v.isoformat()
            elif isinstance(v, Enum):
                processed_values[k] = v.value
        self.form_values = processed_values
        self.form_mode = FormMode(mode)
        self.validate_form()
        self.touched_fields = []

    @rx.event
    def set_form_mode(self, mode: str):
        try:
            self.form_mode = FormMode(mode)
        except ValueError as e:
            logging.exception(f"Error setting form mode: {e}")
            pass
