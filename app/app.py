import reflex as rx
from app.pages.deals.deals_page import (
    deals_list_page,
    deals_add_page,
    deals_review_page,
)
from app.states.deals.deals_state import DealState
from app.states.alerts.alert_state import AlertState
from app.states.ui.ui_state import UIState
from app.states.deal_form_state import DealFormState


def index() -> rx.Component:
    """Root index redirects to deals list."""
    return rx.box(on_mount=rx.redirect("/deals/list"))


def deals_index() -> rx.Component:
    """Deals index redirects to deals list tab."""
    return rx.box(on_mount=rx.redirect("/deals/list"))


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)

# Root route
app.add_page(index, route="/")

# Deals module routes with tabs
app.add_page(
    deals_index,
    route="/deals",
    title="Deals | HDP",
)

app.add_page(
    deals_list_page,
    route="/deals/list",
    on_load=[
        UIState.set_module("deals"),
        UIState.set_tab("list"),
        DealState.load_data,
        AlertState.generate_alerts,
    ],
    title="Deals | HDP",
)

app.add_page(
    deals_add_page,
    route="/deals/add",
    on_load=[
        UIState.set_module("deals"),
        UIState.set_tab("add"),
        DealFormState.reset_form,
    ],
    title="Add Deal | HDP",
)

app.add_page(
    deals_review_page,
    route="/deals/review",
    on_load=[
        UIState.set_module("deals"),
        UIState.set_tab("review"),
        DealState.load_data,
        DealState.on_review_page_load,
    ],
    title="Review Deals | HDP",
)
