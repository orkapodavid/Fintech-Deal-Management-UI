import reflex as rx
from app.states.deals.mixins.list_mixin import DealListMixin
from app.states.deals.mixins.add_mixin import DealAddMixin
from app.states.deals.mixins.review_mixin import DealReviewMixin


class DealState(
    DealListMixin,
    DealAddMixin,
    DealReviewMixin,
    rx.State,
):
    """Main state for Deals section, composing all mixins."""

    @rx.event
    def show_settings(self):
        """Displays a settings toast placeholder."""
        return rx.toast.info(
            "Settings panel is under construction.",
            position="bottom-right",
            duration=3000,
        )

    @rx.event
    def show_notifications(self):
        """Show notifications info."""
        return rx.toast(
            "You have new notifications.", position="bottom-right", duration=2000
        )

    @rx.event
    def logout(self):
        """Simulates user logout."""
        return rx.toast.warning(
            "Logging out...",
            position="bottom-right",
            duration=2000,
        )
