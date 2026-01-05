import reflex as rx
from faker import Faker
import random
from datetime import datetime
from app.states.schema import Alert

fake = Faker()


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
        severities = ["critical", "warning", "system"]
        messages = [
            "Pricing date mismatch detected in Project Phoenix",
            "Compliance flag: Unusual short interest on ticker AAPL",
            "AI confidence score below 60% for secondary shares field",
            "New prospectus document available for daily processing",
            "Regulatory update: CDR Exchange Code requires validation",
            "Market cap threshold exceeded for high-volatility sector",
            "System: Connection established with secure file repository",
        ]
        new_alerts = []
        for i in range(5):
            severity = random.choice(severities)
            alert = Alert(
                id=i,
                severity=severity,
                title=f"{severity.title()} Alert",
                message=random.choice(messages),
                timestamp=datetime.now().isoformat(),
                deal_ticker=None,
                is_dismissed=False,
            )
            new_alerts.append(alert)
        self.alerts = new_alerts

    @rx.var
    def unread_count(self) -> int:
        return len([a for a in self.alerts if not a.get("is_dismissed", False)])