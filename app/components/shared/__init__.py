"""Shared components package exports."""

from app.components.shared.navigation import navigation, nav_item
from app.components.shared.navbar import navbar
from app.components.shared.sidebar import sidebar
from app.components.shared.alert_sidebar import (
    alert_sidebar,
    alert_item,
    format_timestamp_display,
)
from app.components.shared.confirmation_dialog import confirmation_dialog
from app.components.shared.layout import layout, page_layout
from app.components.shared.module_layout import module_layout, sub_tab_link
from app.components.shared.pdf_viewer import (
    Document as PdfDocument,
    Page as PdfPage,
    pdf_viewer_with_nav,
)

__all__ = [
    # Navigation
    "navigation",
    "navbar",
    "nav_item",
    # Sidebar
    "sidebar",
    "alert_sidebar",
    "alert_item",
    "format_timestamp_display",
    # Dialog
    "confirmation_dialog",
    # Layout
    "layout",
    "page_layout",
    # Module Layout
    "module_layout",
    "sub_tab_link",
    # PDF Viewer
    "PdfDocument",
    "PdfPage",
    "pdf_viewer_with_nav",
]
