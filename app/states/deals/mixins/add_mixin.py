import reflex as rx
from datetime import datetime
from app.states.shared.schema import Deal, DealStatus
from app.states.deals.deal_form_state import DealFormState
from app.services.deals.deal_service import DealService
from app.services.deals.file_upload_service import FileUploadService

deal_service = DealService()


class DealAddMixin(rx.State, mixin=True):
    """Mixin for Add Deal logic."""

    upload_tab: str = "upload"
    form_data: dict = {}

    # File upload state
    uploaded_file: dict = {}
    upload_error: str = ""
    is_uploading: bool = False

    @rx.var
    def has_uploaded_file(self) -> bool:
        return bool(self.uploaded_file)

    @rx.event
    def set_upload_tab(self, tab: str):
        self.upload_tab = tab

    @rx.event
    async def on_file_upload(self, files: list[rx.UploadFile]):
        """
        Handle file upload from rx.upload component.

        Args:
            files: List of uploaded file objects
        """
        self.is_uploading = True
        self.upload_error = ""

        service = FileUploadService()

        for f in files:
            try:
                # Read file content
                upload_data = await f.read()
                original_name = f.filename

                # Validate file type
                if not service.validate_file_type(original_name):
                    self.upload_error = f"Invalid file type: {original_name}"
                    continue

                # Save to permanent storage
                self.uploaded_file = await service.save_uploaded_file(
                    data=upload_data, original_name=original_name
                )

            except Exception as e:
                self.upload_error = f"Upload failed: {str(e)}"

        self.is_uploading = False

    @rx.event
    def clear_uploaded_file(self):
        """Clear the uploaded file state."""
        self.uploaded_file = {}
        self.upload_error = ""

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
        """Edit a selected deal by redirecting to the review page."""
        # Check if exactly one deal is selected
        selected_count = len(self.selected_deal_ids)
        if selected_count != 1:
            return rx.toast("Select exactly one deal to edit.", position="bottom-right")

        deal_id = self.selected_deal_ids[0]
        deal = next((d for d in self.deals if d.id == deal_id), None)

        if not deal:
            return rx.toast(
                "Could not find the selected deal.", position="bottom-right"
            )

        # Load the deal into form state for editing
        form_state = await self.get_state(DealFormState)
        form_state.load_deal_for_edit(deal, mode="review")

        # Redirect to the review page with the deal ID
        return rx.redirect(f"/deals/review?id={deal_id}")

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
