import reflex as rx
from typing import Optional
from datetime import datetime
from app.states.schema import Deal, DealStatus
from app.states.deal_form_state import DealFormState
from app.services.deal_service import DealService

deal_service = DealService()


class DealReviewMixin(rx.State, mixin=True):
    """Mixin for Review Deal logic."""

    active_review_deal: Optional[Deal] = None

    @rx.var
    def pending_deals(self) -> list[Deal]:
        # Requires self.deals from ListMixin or Main State
        if not hasattr(self, "deals"):
            return []
        return [d for d in self.deals if d.status == DealStatus.PENDING_REVIEW]

    @rx.var
    def active_deals_count(self) -> int:
        if not hasattr(self, "deals"):
            return 0
        return len([d for d in self.deals if d.status == DealStatus.ACTIVE])

    @rx.event
    async def select_deal_for_review(self, deal_id: str):
        deal = next((d for d in self.deals if d.id == deal_id), None)
        if deal:
            self.active_review_deal = deal
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, "review")
            # In route-based app, we might also want to push route, but
            # if we are just clicking in list page to go to review, we should use rx.link
            # However this event loads the state.
            # If used from DealList, we might want to redirect.
            # But the plan says Review Page deals with query params.
            return rx.redirect(f"/deals/review?id={deal.id}")

    @rx.event
    async def on_review_page_load(self):
        """Handle review page load - check query params to load deal from URL."""
        deal_id = self.router.page.params.get("id")
        if deal_id:
            deal = next((d for d in self.deals if d.id == deal_id), None)
            if deal:
                self.active_review_deal = deal
                form_state = await self.get_state(DealFormState)
                form_state.load_deal_for_edit(deal, "review")
        else:
            self.active_review_deal = None

    @rx.event
    async def approve_current_deal(self):
        if self.active_review_deal:
            deal_id = self.active_review_deal.id
            form_state = await self.get_state(DealFormState)
            updated_values = form_state.form_values

            deal = deal_service.get_deal_by_id(deal_id)
            if deal:
                for k, v in updated_values.items():
                    if v == "":
                        v = None
                    if hasattr(deal, k):
                        setattr(deal, k, v)
                deal.status = DealStatus.ACTIVE
                deal.updated_at = datetime.now().isoformat()
                deal_service.save_deal(deal)

                # Refresh local state
                if hasattr(self, "deals"):
                    self.deals = deal_service.get_deals()

            self.active_review_deal = None
            form_state.reset_form()
            return [
                rx.toast(
                    "Deal approved and activated.",
                    position="bottom-right",
                    duration=3000,
                )
            ]

    @rx.event
    def reject_current_deal(self):
        if self.active_review_deal:
            deal_id = self.active_review_deal.id
            deal_service.delete_deal(deal_id)
            if hasattr(self, "deals"):
                self.deals = deal_service.get_deals()
            self.active_review_deal = None
            # self.form_data = {} # form_data is in AddMixin, maybe should be shared or just ignored here
            return [
                rx.toast(
                    "Deal rejected and removed.", position="bottom-right", duration=3000
                )
            ]
