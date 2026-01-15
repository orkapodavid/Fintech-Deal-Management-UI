"""Module layout component with tab bar for subpages.

Implements the tabbed module layout pattern with navigation, secondary tabs,
content area, and validation alerts sidebar.
"""

import reflex as rx
from app.components.shared.navigation import navigation
from app.components.shared.sidebar import sidebar
from app.states.ui.ui_state import UIState


def sub_tab_link(name: str, tab_id: str, route: str) -> rx.Component:
    """Render a single subtab as a link in the tab bar.

    Args:
        name: Display name for the tab
        tab_id: Tab identifier for active state matching
        route: URL route to navigate to

    Returns:
        Tab link component with active/inactive styling
    """
    is_active = UIState.active_tab == tab_id

    return rx.el.a(
        name,
        href=route,
        on_click=lambda: UIState.set_tab(tab_id),
        class_name=rx.cond(
            is_active,
            "px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600 cursor-pointer",
            "px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 border-transparent hover:border-gray-300 cursor-pointer transition-colors",
        ),
    )


def module_layout(
    content: rx.Component,
    module_name: str,
    tabs: list[dict],
) -> rx.Component:
    """Shared layout wrapper for module pages with a tab bar.

    Args:
        content: The active tab's content component
        module_name: Name of the module (for breadcrumb/header)
        tabs: List of tab definitions [{"name": "Display Name", "id": "tab_id", "route": "/path"}]

    Returns:
        Complete module layout with navigation, tab bar, content, and sidebar
    """
    return rx.el.div(
        # Region 1: Top navigation
        navigation(),
        # Regions 2-4: Main content area
        rx.el.div(
            # Region 3: Contextual workspace (tabs + content)
            rx.el.div(
                # Tab bar
                rx.el.div(
                    rx.foreach(
                        tabs,
                        lambda tab: sub_tab_link(tab["name"], tab["id"], tab["route"]),
                    ),
                    class_name="flex border-b border-gray-200 bg-white px-4",
                ),
                # Main tab content region
                rx.el.div(
                    content,
                    class_name="flex-1 overflow-auto",
                ),
                class_name="flex flex-col flex-1 min-h-0 h-full",
            ),
            # Region 4: Notification/sidebar area (Validation Alerts)
            sidebar(),
            class_name="flex flex-1 overflow-hidden min-h-0 bg-gray-50 w-full",
        ),
        class_name="font-['Inter'] h-screen w-screen bg-gray-50 text-gray-900 flex flex-col overflow-hidden",
    )
