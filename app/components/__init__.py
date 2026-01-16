# Components package exports
# Shared components
from app.components.shared.navigation import navigation
from app.components.shared.navbar import navbar
from app.components.shared.alert_sidebar import alert_sidebar
from app.components.shared.confirmation_dialog import confirmation_dialog

# Deals components
from app.components.deals.deal_form_component import deal_form_component

# Backward compatibility re-exports (deprecated old paths)
# These are kept for files that may still use old imports

__all__ = [
    # Shared
    "navigation",
    "navbar",
    "alert_sidebar",
    "confirmation_dialog",
    # Deals
    "deal_form_component",
]
