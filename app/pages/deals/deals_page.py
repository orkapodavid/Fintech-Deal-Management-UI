"""Deals module page with tabbed layout.

This is the hub component that renders the deals module with tab navigation.
Each tab displays a different view (List, Add, Review) within the shared module layout.
"""

import reflex as rx
from app.components.shared.module_layout import module_layout
from app.pages.deals.list_page import deals_list_view
from app.pages.deals.add_page import deals_add_view
from app.pages.deals.review_page import deals_review_view


# Tab definitions for the deals module
DEALS_TABS = [
    {"name": "List", "id": "list", "route": "/deals/list"},
    {"name": "Add New", "id": "add", "route": "/deals/add"},
    {"name": "Review", "id": "review", "route": "/deals/review"},
]


def deals_list_page() -> rx.Component:
    """Deals list page with tabbed module layout."""
    return module_layout(
        content=deals_list_view(),
        module_name="Deals",
        tabs=DEALS_TABS,
    )


def deals_add_page() -> rx.Component:
    """Deals add page with tabbed module layout."""
    return module_layout(
        content=deals_add_view(),
        module_name="Deals",
        tabs=DEALS_TABS,
    )


def deals_review_page() -> rx.Component:
    """Deals review page with tabbed module layout."""
    return module_layout(
        content=deals_review_view(),
        module_name="Deals",
        tabs=DEALS_TABS,
    )
