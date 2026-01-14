import reflex as rx
from datetime import datetime
from app.states.schema import Deal, DealStatus
from app.states.deal_form_state import DealFormState
from app.services.deal_service import DealService

deal_service = DealService()


class DealAddMixin(rx.State, mixin=True):
    """Mixin for Add Deal logic."""

    upload_tab: str = "upload"
    form_data: dict = {}

    @rx.event
    def set_upload_tab(self, tab: str):
        self.upload_tab = tab

    @rx.event
    def handle_form_change(self, field: str, value: str):
        self.form_data[field] = value

    @rx.event
    def clear_form(self):
        self.form_data = {}
        # In the context of a mixin, we might want to ensure we're accessing the main class's active_review_deal if it exists,
        # but here we might just reset local form data.
        # Dealing with active_review_deal should be handled in the main state or review mixin.
        pass

    @rx.event
    def save_draft(self, form_data: dict):
        self._save_deal(form_data, DealStatus.DRAFT)
        return rx.toast("Deal saved as draft.", position="bottom-right", duration=3000)

    @rx.event
    async def get_form_state_values(self):
        form_state = await self.get_state(DealFormState)
        return form_state.form_values

    @rx.event
    async def submit_new_deal(self, form_data: dict):
        # We need to get values from DealFormState as well since the component uses it
        form_state = await self.get_state(DealFormState)
        merged_data = {**form_state.form_values, **form_data}

        # _save_deal implementation needs to be available.
        # distinct choice: duplicate _save_deal here or expect it in main state.
        # Ideally, _save_deal logic is part of this mixin or shareable.
        update = self._save_deal(merged_data, DealStatus.PENDING_REVIEW)
        return [
            update,
            rx.toast(
                "Deal submitted for review.", position="bottom-right", duration=3000
            ),
        ]

    @rx.event
    async def edit_selected_deal(self):
        # Needs access to selected_deal_ids and deals from ListMixin
        # In Reflex, mixins are combined into one class, so self.selected_deal_ids works if inherited.
        if len(self.selected_deal_ids) != 1:
            return rx.toast("Select exactly one deal to edit.", position="bottom-right")
        deal_id = self.selected_deal_ids[0]
        deal = next((d for d in self.deals if d.id == deal_id), None)
        if deal:
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, mode="edit")
            return rx.redirect(f"/deals/add?mode=edit&id={deal_id}")

    def _save_deal(self, form_data: dict, status: DealStatus):
        processed_data = form_data.copy()
        bool_fields = ["flag_bought", "flag_clean_up", "flag_top_up"]
        for field in bool_fields:
            val = processed_data.get(field)
            processed_data[field] = val == "on" or val is True
        float_fields = [
            "shares_amount",
            "offering_price",
            "market_cap",
            "avg_volume",
            "warrants_strike",
        ]
        for field in float_fields:
            if processed_data.get(field) == "":
                processed_data[field] = None
        ticker = processed_data.get("ticker")
        if not ticker:
            import random
            import string

            ticker = "".join(random.choices(string.ascii_uppercase, k=4))
            processed_data["ticker"] = ticker

        now = datetime.now().isoformat()

        deal_id = processed_data.get("id")
        current_deal = None

        if deal_id:
            current_deal = deal_service.get_deal_by_id(deal_id)

        if current_deal is None:
            current_deal = deal_service.get_deal_by_ticker(ticker)

        if current_deal:
            for k, v in processed_data.items():
                if hasattr(current_deal, k):
                    setattr(current_deal, k, v)
            current_deal.status = status
            current_deal.updated_at = now
            deal_service.save_deal(current_deal)
        else:
            processed_data["status"] = status
            processed_data["created_at"] = now
            processed_data["updated_at"] = now
            if "ai_confidence_score" not in processed_data:
                processed_data["ai_confidence_score"] = (
                    100 if status == DealStatus.DRAFT else 85
                )
            new_deal = Deal(**processed_data)
            deal_service.save_deal(new_deal)

        # Update the deals list if we are in the main state context
        if hasattr(self, "deals"):
            self.deals = deal_service.get_deals()

        return rx.noop()
