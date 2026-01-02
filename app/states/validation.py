from typing import Optional
import logging
from pydantic import BaseModel
from datetime import datetime
import re


class ValidationResult(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None


class ValidationService:
    STRUCTURES = ["IPO", "M&A", "Spin-off", "Follow-on", "Convertible"]
    SECTORS = [
        "Technology",
        "Healthcare",
        "Finance",
        "Energy",
        "Consumer",
        "Industrials",
        "Materials",
        "Utilities",
        "Real Estate",
    ]
    COUNTRIES = [
        "USA",
        "UK",
        "Germany",
        "Canada",
        "Singapore",
        "France",
        "Japan",
        "China",
        "India",
        "Australia",
    ]

    @staticmethod
    def validate_field(
        field_name: str,
        value: str | int | float | bool | None,
        all_values: dict[str, str | int | float | bool | None],
    ) -> ValidationResult:
        str_val = str(value).strip() if value is not None else ""
        if field_name == "ticker":
            if not str_val:
                return ValidationResult(
                    is_valid=False, error_message="Ticker is required"
                )
            if not re.match("^[A-Z0-9 ]{2,10}$", str_val):
                return ValidationResult(
                    is_valid=False,
                    error_message="Ticker must be 2-10 uppercase alphanumeric characters",
                )
        if field_name == "structure":
            if not str_val:
                return ValidationResult(
                    is_valid=False, error_message="Structure is required"
                )
            if str_val not in ValidationService.STRUCTURES:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Structure must be one of: {', '.join(ValidationService.STRUCTURES)}",
                )
        if field_name == "offering_price":
            is_bought = str(all_values.get("flag_bought", "")).lower() in [
                "true",
                "on",
                "1",
            ]
            if is_bought and (not str_val):
                return ValidationResult(
                    is_valid=False,
                    error_message="Offering price is required for Bought Deals",
                )
        if field_name in ["warrants_strike", "warrants_exp"]:
            w_min = all_values.get("warrants_min")
            try:
                if w_min and float(w_min) > 0 and (not str_val):
                    return ValidationResult(
                        is_valid=False,
                        error_message=f"{field_name.replace('_', ' ').title()} required when warrants exist",
                    )
            except ValueError as e:
                logging.exception(f"Error validating warrant field {field_name}: {e}")
                pass
        if field_name == "pricing_date":
            announce_date = all_values.get("announce_date")
            if str_val and announce_date:
                try:
                    p_date = datetime.strptime(str_val, "%Y-%m-%d")
                    a_date = datetime.strptime(announce_date, "%Y-%m-%d")
                    if p_date < a_date:
                        return ValidationResult(
                            is_valid=False,
                            error_message="Pricing date cannot be before announce date",
                        )
                except ValueError as e:
                    logging.exception(f"Error validating pricing date range: {e}")
                    pass
        if field_name in [
            "shares_amount",
            "offering_price",
            "market_cap",
            "price_on_pricing_date",
            "vol_on_pricing_date",
            "offer_price_usd",
            "gross_spread",
            "net_purchase_price",
            "primary_shares",
            "secondary_shares",
        ]:
            if str_val:
                try:
                    num_val = float(str_val)
                    if num_val < 0:
                        return ValidationResult(
                            is_valid=False, error_message="Value must be positive"
                        )
                    if field_name == "shares_amount" and num_val > 1000:
                        return ValidationResult(
                            is_valid=False,
                            error_message="Check units (expected millions)",
                        )
                except ValueError as e:
                    logging.exception(
                        f"Error validating numeric field {field_name}: {e}"
                    )
                    return ValidationResult(
                        is_valid=False, error_message="Must be a valid number"
                    )
        if field_name in ["fee_percent", "inst_own_pct"]:
            if str_val:
                try:
                    num_val = float(str_val)
                    if not 0 <= num_val <= 100:
                        return ValidationResult(
                            is_valid=False,
                            error_message="Percentage must be between 0-100",
                        )
                except ValueError as e:
                    logging.exception(
                        f"Error validating percentage field {field_name}: {e}"
                    )
                    return ValidationResult(
                        is_valid=False, error_message="Must be a valid number"
                    )
        if field_name in ["pricing_date", "announce_date", "warrants_exp", "pmi_date"]:
            if str_val:
                try:
                    datetime.strptime(str_val, "%Y-%m-%d")
                except ValueError as e:
                    logging.exception(f"Error parsing date field {field_name}: {e}")
                    return ValidationResult(
                        is_valid=False, error_message="Invalid date format (YYYY-MM-DD)"
                    )
        if field_name == "country":
            if str_val and str_val not in ValidationService.COUNTRIES:
                return ValidationResult(
                    is_valid=False, error_message=f"Invalid country selection"
                )
        if field_name == "sector":
            if str_val and str_val not in ValidationService.SECTORS:
                return ValidationResult(
                    is_valid=False, error_message=f"Invalid sector selection"
                )
        return ValidationResult(is_valid=True)

    @staticmethod
    def validate_all(
        form_data: dict[str, str | int | float | bool | None],
    ) -> dict[str, ValidationResult]:
        results = {}
        fields_to_check = set(form_data.keys()) | {
            "ticker",
            "structure",
            "offering_price",
            "warrants_strike",
            "warrants_exp",
            "pricing_date",
        }
        for field in fields_to_check:
            results[field] = ValidationService.validate_field(
                field, form_data.get(field), form_data
            )
        try:
            total = float(form_data.get("shares_amount") or 0)
            prim = float(form_data.get("primary_shares") or 0)
            sec = float(form_data.get("secondary_shares") or 0)
            if total > 0 and prim > 0 and (sec > 0):
                if abs(total - (prim + sec)) > total * 0.01:
                    if results.get(
                        "shares_amount", ValidationResult(is_valid=True)
                    ).is_valid:
                        results["shares_amount"] = ValidationResult(
                            is_valid=False,
                            error_message=f"Total ({total}) mismatch with Prim+Sec ({prim + sec})",
                        )
        except ValueError as e:
            logging.exception(
                f"Error calculating total shares for cross-validation: {e}"
            )
            pass
        return results

    @staticmethod
    def is_form_valid(validation_results: dict[str, ValidationResult]) -> bool:
        return all((r.is_valid for r in validation_results.values()))