import reflex as rx


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.el.a(
        text,
        href=url,
        class_name="text-sm font-medium text-gray-300 hover:text-white transition-colors px-3 py-2 rounded-md hover:bg-gray-800",
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
                        "NYC-04",
                        class_name="ml-2 text-xs font-mono text-gray-400 border border-gray-700 rounded px-1.5 py-0.5",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    navbar_link("Deals", "/deals"),
                    navbar_link("Add New Deals", "/add"),
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
                        class_name="bg-gray-900 border border-gray-700 text-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-64 pl-10 p-2 placeholder-gray-500",
                    ),
                    class_name="relative hidden lg:block mr-6",
                ),
                rx.icon(
                    "bell",
                    class_name="w-5 h-5 text-gray-400 hover:text-white cursor-pointer mr-4",
                ),
                rx.icon(
                    "settings",
                    class_name="w-5 h-5 text-gray-400 hover:text-white cursor-pointer mr-4",
                ),
                rx.el.div(
                    rx.icon("user", class_name="w-5 h-5 text-gray-800"),
                    class_name="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center border border-gray-600 cursor-pointer",
                ),
                class_name="flex items-center",
            ),
            class_name="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between",
        ),
        class_name="bg-[#0f1115] border-b border-gray-800 sticky top-0 z-50",
    )