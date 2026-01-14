"""Layout wrapper component for consistent page structure."""

import reflex as rx
from app.components.shared.navigation import navigation
from app.components.shared.sidebar import sidebar


def page_layout(content: rx.Component, with_sidebar: bool = True) -> rx.Component:
    """Wrap page content with navigation and optional sidebar.

    Args:
        content: The main page content component
        with_sidebar: Whether to include the alert sidebar (default True)

    Returns:
        Complete page layout with navigation and content
    """
    if with_sidebar:
        return rx.el.div(
            navigation(),
            rx.el.div(
                rx.el.main(
                    content,
                    class_name="flex-1 overflow-auto",
                ),
                sidebar(),
                class_name="flex flex-1 overflow-hidden",
            ),
            class_name="font-['Inter'] min-h-screen bg-gray-50 text-gray-900 flex flex-col",
        )
    else:
        return rx.el.div(
            navigation(),
            rx.el.main(
                content,
                class_name="flex-1 overflow-auto",
            ),
            class_name="font-['Inter'] min-h-screen bg-gray-50 text-gray-900 flex flex-col",
        )


def layout(content: rx.Component) -> rx.Component:
    """Simple layout wrapper (backward compatibility with app.py).

    Args:
        content: The main page content component

    Returns:
        Complete page layout with navigation
    """
    return rx.el.div(
        navigation(),
        content,
        class_name="font-['Inter'] min-h-screen bg-gray-50 text-gray-900",
    )
