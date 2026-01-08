import reflex as rx
from app.config import VERSION
from app.states.deal_state import DealState
from app.states.deal_form_state import DealFormState
from app.states.alert_state import AlertState


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.el.a(
        text,
        href=url,
        class_name="text-sm font-medium text-gray-300 hover:text-white transition-colors px-3 py-2 rounded-md hover:bg-gray-800",
    )


def add_new_deals_link() -> rx.Component:
    """Special link for 'Add New Deals' that resets the form before navigating."""
    return rx.el.button(
        "Add New Deals",
        on_click=[DealFormState.reset_form, rx.redirect("/add")],
        class_name="text-sm font-medium text-gray-300 hover:text-white transition-colors px-3 py-2 rounded-md hover:bg-gray-800 cursor-pointer",
    )


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "HDP", class_name="text-xl font-bold text-white tracking-tight"
                    ),
                    rx.el.span(
                        f"v{VERSION}",
                        class_name="ml-2 text-xs font-mono text-gray-400 border border-gray-700 rounded px-1.5 py-0.5",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    navbar_link("Deals", "/deals"),
                    add_new_deals_link(),
                    navbar_link("Review AI Input", "/review"),
                    class_name="hidden md:flex items-center space-x-4 ml-10",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="w-4 h-4 text-gray-400 absolute left-3 top-2.5",
                    ),
                    rx.el.input(
                        placeholder="Search deals, tickers...",
                        on_change=DealState.set_search_query.debounce(300),
                        class_name="bg-gray-900 border border-gray-700 text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-64 pl-10 p-2 placeholder-gray-500",
                        default_value=DealState.search_query,
                    ),
                    class_name="relative hidden lg:block mr-6",
                ),
                rx.el.button(
                    rx.icon(
                        "refresh-cw",
                        class_name="w-5 h-5 text-gray-400 group-hover:text-white transition-colors",
                    ),
                    on_click=DealState.refresh_data,
                    class_name="group p-2 rounded-full hover:bg-gray-800 transition-colors mr-2",
                    title="Refresh Data",
                ),
                rx.el.button(
                    rx.el.div(
                        rx.icon(
                            "bell",
                            class_name="w-5 h-5 text-gray-400 group-hover:text-white transition-colors",
                        ),
                        rx.cond(
                            AlertState.unread_count > 0,
                            rx.el.span(
                                AlertState.unread_count,
                                class_name="absolute top-1.5 right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-[#0f1115]",
                            ),
                            None,
                        ),
                        class_name="relative",
                    ),
                    on_click=AlertState.toggle_sidebar,
                    class_name="group p-2 rounded-full hover:bg-gray-800 transition-colors mx-3",
                    title="Notifications",
                ),
                rx.el.button(
                    rx.icon(
                        "settings",
                        class_name="w-5 h-5 text-gray-400 group-hover:text-white transition-colors",
                    ),
                    on_click=DealState.show_settings,
                    class_name="group p-2 rounded-full hover:bg-gray-800 transition-colors mx-3",
                    title="Settings",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("user", class_name="w-5 h-5 stroke-gray-800"),
                        class_name="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center border border-gray-600 hover:border-gray-400 transition-colors",
                    ),
                    class_name="relative ml-2 group cursor-pointer mx-3",
                    on_click=DealState.logout,
                    title="Log Out (Demo)",
                ),
                class_name="flex items-center",
            ),
            class_name="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between",
        ),
        class_name="bg-[#0f1115] border-b border-gray-800 sticky top-0 z-50",
    )