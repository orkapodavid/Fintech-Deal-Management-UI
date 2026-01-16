import reflex as rx
from app.states.shared.schema import Alert
from app.services.alerts.alert_service import AlertService

alert_service = AlertService()


class AlertState(rx.State):
    alerts: list[Alert] = []
    show_sidebar: bool = True

    @rx.event
    def toggle_sidebar(self):
        self.show_sidebar = not self.show_sidebar

    @rx.event
    def dismiss_alert(self, alert_id: int):
        self.alerts = [a for a in self.alerts if a.id != alert_id]

    @rx.event
    def generate_alerts(self):
        if self.alerts:
            return
        self.alerts = alert_service.get_alerts()

    @rx.var
    def unread_count(self) -> int:
        return len([a for a in self.alerts if not a.get("is_dismissed", False)])
