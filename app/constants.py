"""Design tokens and constants for the Fintech Deal Management UI."""

# =============================================================================
# COLOR PALETTE
# =============================================================================

# Primary colors (dark theme for navbar)
COLORS = {
    "primary_dark": "#0f1115",
    "primary_border": "#374151",  # gray-700
    "primary_text": "#ffffff",
    "primary_text_muted": "#9ca3af",  # gray-400
    # Background colors
    "bg_main": "#f9fafb",  # gray-50
    "bg_white": "#ffffff",
    "bg_dark": "#0f1115",
    # Text colors
    "text_primary": "#111827",  # gray-900
    "text_secondary": "#6b7280",  # gray-500
    "text_muted": "#9ca3af",  # gray-400
    # Semantic colors
    "success": "#10b981",  # green-500
    "warning": "#f59e0b",  # amber-500
    "error": "#ef4444",  # red-500
    "info": "#3b82f6",  # blue-500
    # Status badge colors
    "status_active_bg": "#dcfce7",  # green-100
    "status_active_text": "#166534",  # green-800
    "status_pending_bg": "#fef3c7",  # amber-100
    "status_pending_text": "#92400e",  # amber-800
    "status_draft_bg": "#f3f4f6",  # gray-100
    "status_draft_text": "#374151",  # gray-700
}

# Alert severity colors
ALERT_COLORS = {
    "critical": {
        "border": "border-l-red-500",
        "badge_text": "text-red-700",
        "badge_bg": "bg-red-50",
    },
    "warning": {
        "border": "border-l-orange-400",
        "badge_text": "text-orange-700",
        "badge_bg": "bg-orange-50",
    },
    "system": {
        "border": "border-l-blue-500",
        "badge_text": "text-blue-700",
        "badge_bg": "bg-blue-50",
    },
    "default": {
        "border": "border-l-gray-300",
        "badge_text": "text-gray-700",
        "badge_bg": "bg-gray-50",
    },
}

# =============================================================================
# DIMENSIONS
# =============================================================================

DIMENSIONS = {
    # Navigation
    "navbar_height": "64px",
    "navbar_height_class": "h-16",
    # Sidebar
    "sidebar_width": "320px",
    "sidebar_width_collapsed": "64px",
    "sidebar_width_class": "w-80",
    "sidebar_collapsed_class": "w-16",
    # Content
    "max_content_width": "1920px",
    "content_padding": "16px",
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================

TYPOGRAPHY = {
    "font_family": "Inter",
    "font_family_mono": "monospace",
}

# Font size classes
FONT_SIZES = {
    "xs": "text-xs",  # 12px
    "sm": "text-sm",  # 14px
    "base": "text-base",  # 16px
    "lg": "text-lg",  # 18px
    "xl": "text-xl",  # 20px
}

# =============================================================================
# COMMON TAILWIND CLASS COMBINATIONS
# =============================================================================

# Button styles
BUTTON_STYLES = {
    "primary": "bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-lg font-medium transition-colors",
    "secondary": "bg-gray-100 text-gray-700 hover:bg-gray-200 px-4 py-2 rounded-lg font-medium transition-colors",
    "ghost": "text-gray-600 hover:text-gray-900 hover:bg-gray-100 px-3 py-2 rounded-md transition-colors",
    "icon": "p-2 rounded-full hover:bg-gray-800 transition-colors",
}

# Input styles
INPUT_STYLES = {
    "default": "bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
    "search": "bg-gray-900 border border-gray-700 text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-64 pl-10 p-2 placeholder-gray-500",
}

# Card styles
CARD_STYLES = {
    "default": "bg-white border border-gray-200 rounded-lg shadow-sm",
    "hover": "bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow",
}

# Table styles
TABLE_STYLES = {
    "header_cell": "px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
    "data_cell": "px-4 py-3 text-sm text-gray-900",
    "row": "border-b border-gray-100 hover:bg-gray-50 transition-colors",
}

# =============================================================================
# MODULE CONFIGURATION
# =============================================================================

# Module tabs configuration for UIState
MODULE_TABS = {
    "deals": {
        "label": "Deals",
        "tabs": [
            {"id": "list", "label": "All Deals", "route": "/deals"},
            {"id": "add", "label": "Add New", "route": "/deals/add"},
            {"id": "review", "label": "Review AI Input", "route": "/deals/review"},
        ],
    },
}

# Default module
DEFAULT_MODULE = "deals"
DEFAULT_TAB = "list"
