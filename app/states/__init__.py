# States package exports
# Shared
from app.states.shared.schema import Deal, DealStatus, Alert

# Deals
from app.states.deals.deals_state import DealState
from app.states.deals.deal_form_state import DealFormState, FormMode

# Alerts
from app.states.alerts.alert_state import AlertState

# UI
from app.states.ui.ui_state import UIState

# Backward compatibility re-exports (deprecated old paths)
# These maintain backward compatibility for files using old import paths
# e.g., `from app.states.schema import Deal` still works
# e.g., `from app.states.deal_form_state import DealFormState` still works

__all__ = [
    # Shared
    "Deal",
    "DealStatus",
    "Alert",
    # Deals
    "DealState",
    "DealFormState",
    "FormMode",
    # Alerts
    "AlertState",
    # UI
    "UIState",
]
