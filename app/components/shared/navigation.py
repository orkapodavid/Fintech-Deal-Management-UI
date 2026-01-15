"""Navigation component for the application (Region 1).

Implements the shared top navigation bar matching the architecture guide
Section 3.4 "Region 1: Navigation Component".
"""

import reflex as rx
from app.states.ui.ui_state import UIState
from app.states.alerts.alert_state import AlertState
from app.states.deals.deals_state import DealState
from app.states.deal_form_state import DealFormState
from app.config import VERSION


def nav_item(name: str, icon: str, route: str, module_id: str) -> rx.Component:
    """Single navigation item with active state styling.

    Args:
        name: Display name for the nav item
        icon: Lucide icon name
        route: URL route to navigate to
        module_id: Module identifier for active state matching

    Returns:
        Navigation item component with active/inactive styling
    """
    is_active = UIState.active_module == module_id

    return rx.el.a(
        rx.icon(
            icon,
            size=16,
            class_name=rx.cond(
                is_active,
                "text-white",
                "text-gray-400 group-hover:text-gray-200",
            ),
        ),
        rx.el.span(
            name,
            class_name=rx.cond(
                is_active,
                "text-sm ml-2 hidden md:inline text-white font-medium",
                "text-sm ml-2 hidden md:inline text-gray-300 group-hover:text-white",
            ),
        ),
        href=route,
        on_click=lambda: UIState.set_module(module_id),
        class_name=rx.cond(
            is_active,
            "group flex items-center px-4 py-2 bg-gray-700 rounded-lg cursor-pointer",
            "group flex items-center px-4 py-2 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer",
        ),
    )


def add_deals_nav_item() -> rx.Component:
    """Special nav item for 'Add New' that resets the form before navigating."""
    is_active = UIState.active_module == "add"

    return rx.el.button(
        rx.icon(
            "plus",
            size=16,
            class_name=rx.cond(
                is_active,
                "text-white",
                "text-gray-400 group-hover:text-gray-200",
            ),
        ),
        rx.el.span(
            "Add New",
            class_name=rx.cond(
                is_active,
                "text-sm ml-2 hidden md:inline text-white font-medium",
                "text-sm ml-2 hidden md:inline text-gray-300 group-hover:text-white",
            ),
        ),
        on_click=[
            UIState.set_module("add"),
            DealFormState.reset_form,
            rx.redirect("/deals/add"),
        ],
        class_name=rx.cond(
            is_active,
            "group flex items-center px-4 py-2 bg-gray-700 rounded-lg cursor-pointer",
            "group flex items-center px-4 py-2 hover:bg-gray-800 rounded-lg transition-colors cursor-pointer",
        ),
    )


def navigation() -> rx.Component:
    """Top navigation bar (Region 1) matching the architecture guide styles.

    Fixed height 56px, dark background, with brand, module navigation, and action buttons.
    """
    return rx.el.nav(
        rx.el.div(
            # Left: Brand
            rx.el.div(
                rx.icon("briefcase", size=22, class_name="text-blue-400"),
                rx.el.span(
                    "HDP",
                    class_name="font-bold text-lg ml-2 text-white",
                ),
                rx.el.span(
                    f"v{VERSION}",
                    class_name="ml-3 text-xs font-mono text-gray-500 border border-gray-700 rounded px-1.5 py-0.5",
                ),
                class_name="flex items-center",
            ),
            # Center: Module navigation items
            rx.el.div(
                nav_item("Deals", "folder", "/deals/list", "deals"),
                class_name="flex items-center gap-2 ml-8",
            ),
            # Right: Actions (search, refresh, notifications, settings, user)
            rx.el.div(
                # Search input (hidden on smaller screens)
                rx.el.div(
                    rx.icon(
                        "search",
                        size=16,
                        class_name="text-gray-500 absolute left-3 top-2.5",
                    ),
                    rx.el.input(
                        placeholder="Search deals...",
                        on_change=DealState.set_search_query.debounce(300),
                        class_name="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-48 pl-9 py-2 placeholder-gray-500",
                        default_value=DealState.search_query,
                    ),
                    class_name="relative hidden lg:block mr-4",
                ),
                # Refresh button
                rx.el.button(
                    rx.icon(
                        "refresh-cw",
                        size=18,
                        class_name="text-gray-400 group-hover:text-white",
                    ),
                    on_click=DealState.refresh_data,
                    class_name="group p-2 hover:bg-gray-800 rounded-lg transition-colors",
                    title="Refresh Data",
                ),
                # Notification bell with badge
                rx.el.button(
                    rx.el.div(
                        rx.icon(
                            "bell",
                            size=18,
                            class_name="text-gray-400 group-hover:text-white",
                        ),
                        rx.cond(
                            AlertState.unread_count > 0,
                            rx.el.span(
                                AlertState.unread_count,
                                class_name="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white",
                            ),
                            None,
                        ),
                        class_name="relative",
                    ),
                    on_click=[UIState.toggle_sidebar, AlertState.toggle_sidebar],
                    class_name="group p-2 hover:bg-gray-800 rounded-lg transition-colors ml-1",
                    title="Notifications",
                ),
                # Settings button
                rx.el.button(
                    rx.icon(
                        "settings",
                        size=18,
                        class_name="text-gray-400 group-hover:text-white",
                    ),
                    on_click=DealState.show_settings,
                    class_name="group p-2 hover:bg-gray-800 rounded-lg transition-colors ml-1",
                    title="Settings",
                ),
                # User profile button
                rx.el.button(
                    rx.icon(
                        "user",
                        size=18,
                        class_name="text-gray-400 group-hover:text-white",
                    ),
                    on_click=DealState.logout,
                    class_name="group p-2 hover:bg-gray-800 rounded-lg transition-colors ml-1",
                    title="Log Out (Demo)",
                ),
                class_name="flex items-center ml-auto",
            ),
            class_name="flex items-center w-full px-4",
        ),
        class_name="h-14 bg-[#0f1115] border-b border-gray-800 text-white flex items-center shrink-0",
    )


# Backward compatibility alias
navbar = navigation
