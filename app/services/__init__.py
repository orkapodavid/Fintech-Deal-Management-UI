# Services package exports
# Re-exports for backward compatibility

# Deals
from app.services.deals.deal_service import DealService

# Alerts
from app.services.alerts.alert_service import AlertService

__all__ = [
    "DealService",
    "AlertService",
]
