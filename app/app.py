import reflex as rx
from app.components.shared import layout
from app.pages.deals.list_page import deals_list_page
from app.pages.deals.add_page import deals_add_page
from app.pages.deals.review_page import deals_review_page
from app.states.deals.deals_state import DealState
from app.states.alerts.alert_state import AlertState


def deals_page_wrapper() -> rx.Component:
    return layout(deals_list_page())


def add_page_wrapper() -> rx.Component:
    return layout(deals_add_page())


def review_page_wrapper() -> rx.Component:
    return layout(deals_review_page())


def index() -> rx.Component:
    return rx.box(on_mount=rx.redirect("/deals"))


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

app.add_page(index, route="/")

app.add_page(
    deals_page_wrapper,
    route="/deals",
    on_load=[DealState.load_data, AlertState.generate_alerts],
    title="Deals | HDP",
)

app.add_page(
    add_page_wrapper,
    route="/deals/add",
    title="Add Deal | HDP",
)

app.add_page(
    review_page_wrapper,
    route="/deals/review",
    on_load=[DealState.load_data, DealState.on_review_page_load],
    title="Review Deals | HDP",
)
