from typing import List
from datetime import datetime
import random
from app.states.schema import Alert

class AlertService:
    def get_alerts(self) -> List[Alert]:
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
        return new_alerts
