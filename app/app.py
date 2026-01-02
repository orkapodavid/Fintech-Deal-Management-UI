import reflex as rx
from app.components.navbar import navbar
from app.pages.deals_page import deals_page
from app.pages.add_page import add_page
from app.pages.review_page import review_page
from app.states.deal_state import DealState
from app.states.alert_state import AlertState


def layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        content,
        class_name="font-['Inter'] min-h-screen bg-gray-50 text-gray-900",
    )


def index() -> rx.Component:
    return layout(deals_page())


def add() -> rx.Component:
    return layout(add_page())


def review() -> rx.Component:
    return layout(review_page())


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
app.add_page(
    index, route="/deals", on_load=[DealState.load_data, AlertState.generate_alerts]
)
app.add_page(add, route="/add")
app.add_page(review, route="/review", on_load=DealState.load_data)
app.add_page(
    index, route="/", on_load=[DealState.load_data, AlertState.generate_alerts]
)