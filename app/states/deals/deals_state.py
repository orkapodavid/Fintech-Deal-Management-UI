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
        return rx.toast(
            "Settings panel is under construction.",
            position="bottom-right",
            duration=3000,
            style={
                "background-color": "#F3F4F6",
                "color": "#374151",
                "border": "1px solid #E5E7EB",
            },
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
        return rx.toast(
            "Logging out...",
            position="bottom-right",
            duration=2000,
            style={
                "background-color": "#FEF2F2",
                "color": "#991B1B",
                "border": "1px solid #FECACA",
            },
        )
