"""Global UI state for navigation, sidebar, and cross-cutting UI concerns."""

import reflex as rx
from app.constants import MODULE_TABS, DEFAULT_MODULE, DEFAULT_TAB


class UIState(rx.State):
    """Global UI state managing navigation and sidebar visibility."""

    # Active navigation
    active_module: str = DEFAULT_MODULE
    active_tab: str = DEFAULT_TAB

    # Sidebar state
    is_sidebar_open: bool = False

    # Mobile menu state
    is_mobile_menu_open: bool = False

    @rx.var(cache=True)
    def current_module_config(self) -> dict:
        """Get the configuration for the current module."""
        return MODULE_TABS.get(self.active_module, {})

    @rx.var(cache=True)
    def current_tabs(self) -> list:
        """Get the tabs for the current module."""
        config = self.current_module_config
        return config.get("tabs", [])

    @rx.event
    def set_module(self, module: str):
        """Set the active module and reset to default tab."""
        self.active_module = module
        module_config = MODULE_TABS.get(module, {})
        tabs = module_config.get("tabs", [])
        if tabs:
            self.active_tab = tabs[0].get("id", DEFAULT_TAB)

    @rx.event
    def set_tab(self, tab: str):
        """Set the active tab within the current module."""
        self.active_tab = tab

    @rx.event
    def toggle_sidebar(self):
        """Toggle the sidebar visibility."""
        self.is_sidebar_open = not self.is_sidebar_open

    @rx.event
    def open_sidebar(self):
        """Open the sidebar."""
        self.is_sidebar_open = True

    @rx.event
    def close_sidebar(self):
        """Close the sidebar."""
        self.is_sidebar_open = False

    @rx.event
    def toggle_mobile_menu(self):
        """Toggle mobile menu visibility."""
        self.is_mobile_menu_open = not self.is_mobile_menu_open

    @rx.event
    def close_mobile_menu(self):
        """Close the mobile menu."""
        self.is_mobile_menu_open = False
