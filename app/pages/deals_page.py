import reflex as rx
from app.states.deal_state import DealState
from app.components.alert_sidebar import alert_sidebar


def badge(text: str, color_scheme: str = "gray") -> rx.Component:
    colors = {
        "gray": "bg-gray-100 text-gray-800",
        "blue": "bg-blue-100 text-blue-800",
        "green": "bg-green-100 text-green-800",
        "purple": "bg-purple-100 text-purple-800",
        "yellow": "bg-yellow-100 text-yellow-800",
    }
    return rx.el.span(
        text,
        class_name=f"inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold tracking-wide {colors.get(color_scheme, 'bg-gray-100 text-gray-800')}",
    )


def deals_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.button(
                        rx.icon("filter", size=16, class_name="mr-2"),
                        "Filter",
                        class_name="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none transition-colors",
                    ),
                    rx.el.div(
                        rx.el.span(
                            "Sector: Tech",
                            rx.icon(
                                "x",
                                size=12,
                                class_name="ml-1.5 text-blue-500 hover:text-blue-700",
                            ),
                            class_name="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100 mr-2 cursor-pointer hover:bg-blue-100 transition-colors",
                        ),
                        rx.el.span(
                            "Date: Today",
                            rx.icon(
                                "x",
                                size=12,
                                class_name="ml-1.5 text-gray-500 hover:text-gray-700",
                            ),
                            class_name="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-50 text-gray-700 border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors",
                        ),
                        rx.el.button(
                            "+ Add Filter",
                            class_name="ml-2 text-xs font-medium text-blue-600 hover:text-blue-800",
                        ),
                        class_name="ml-4 flex items-center",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("download", size=16, class_name="mr-2"),
                        "Export",
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 mr-4 transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("pencil", size=16, class_name="mr-2"),
                        "Edit Selected",
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 mr-4 transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", size=16, class_name="mr-2"),
                        "Delete",
                        on_click=DealState.delete_selected_deals,
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors",
                    ),
                    class_name="flex items-center",
                ),
                class_name="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm z-10",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                rx.el.input(
                                    type="checkbox",
                                    checked=DealState.all_selected,
                                    on_change=lambda _: DealState.toggle_select_all(),
                                    class_name="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4",
                                ),
                                class_name="pl-6 pr-3 py-3 text-left w-10 bg-gray-50",
                            ),
                            rx.el.th(
                                "Ticker",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Structure",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Flags",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Shares (M)",
                                class_name="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Offer Price",
                                class_name="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Pricing Date",
                                class_name="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Announce Date",
                                class_name="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Sector",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Country",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Mkt Cap (M)",
                                class_name="px-3 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            rx.el.th(
                                "Conf.",
                                class_name="px-3 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            class_name="border-b border-gray-200",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            DealState.paginated_deals,
                            lambda deal: rx.el.tr(
                                rx.el.td(
                                    rx.el.input(
                                        type="checkbox",
                                        checked=DealState.selected_deal_ids.contains(
                                            deal.ticker
                                        ),
                                        on_change=lambda _: DealState.toggle_select_deal(
                                            deal.ticker
                                        ),
                                        class_name="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4",
                                    ),
                                    class_name="pl-6 pr-3 py-4 whitespace-nowrap w-10",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        deal.ticker,
                                        class_name="font-semibold text-blue-600 cursor-pointer hover:underline",
                                    ),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm",
                                ),
                                rx.el.td(
                                    deal.structure,
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500",
                                ),
                                rx.el.td(
                                    rx.el.div(
                                        rx.cond(
                                            deal.flag_clean_up,
                                            badge("CLEAN", "green"),
                                            None,
                                        ),
                                        rx.cond(
                                            deal.flag_bought,
                                            badge("BOUGHT", "blue"),
                                            None,
                                        ),
                                        rx.cond(
                                            deal.status == "pending_review",
                                            badge("PENDING", "yellow"),
                                            None,
                                        ),
                                        rx.cond(
                                            deal.flag_top_up,
                                            badge("TOP", "purple"),
                                            None,
                                        ),
                                        class_name="flex flex-wrap gap-1 max-w-[150px]",
                                    ),
                                    class_name="px-3 py-4",
                                ),
                                rx.el.td(
                                    deal.shares_amount.to_string(),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-mono",
                                ),
                                rx.el.td(
                                    f"${deal.offering_price}",
                                    class_name=rx.cond(
                                        deal.offering_price > 50,
                                        "px-3 py-4 whitespace-nowrap text-sm font-bold text-green-700 text-right font-mono",
                                        "px-3 py-4 whitespace-nowrap text-sm font-bold text-red-600 text-right font-mono",
                                    ),
                                ),
                                rx.el.td(
                                    deal.pricing_date.to_string(),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500 text-right",
                                ),
                                rx.el.td(
                                    deal.announce_date.to_string(),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500 text-right",
                                ),
                                rx.el.td(
                                    deal.sector,
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500",
                                ),
                                rx.el.td(
                                    deal.country,
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500",
                                ),
                                rx.el.td(
                                    f"${deal.market_cap}",
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono",
                                ),
                                rx.el.td(
                                    rx.el.div(
                                        rx.el.span(
                                            deal.ai_confidence_score.to_string() + "%",
                                            class_name=rx.cond(
                                                deal.ai_confidence_score >= 80,
                                                "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
                                                rx.cond(
                                                    deal.ai_confidence_score >= 50,
                                                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800",
                                                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800",
                                                ),
                                            ),
                                        ),
                                        class_name="flex justify-center",
                                    ),
                                    class_name="px-3 py-4 whitespace-nowrap text-center",
                                ),
                                class_name="bg-white border-b hover:bg-blue-50 transition-colors",
                            ),
                        ),
                        class_name="divide-y divide-gray-200",
                    ),
                    class_name="min-w-full divide-y divide-gray-200",
                ),
                class_name="overflow-auto flex-1",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Showing ",
                        rx.el.span(
                            f"{(DealState.current_page - 1) * DealState.items_per_page + 1}",
                            class_name="font-medium",
                        ),
                        "-",
                        rx.el.span(
                            rx.cond(
                                DealState.current_page * DealState.items_per_page
                                > DealState.filtered_deals.length(),
                                DealState.filtered_deals.length(),
                                DealState.current_page * DealState.items_per_page,
                            ),
                            class_name="font-medium",
                        ),
                        " of ",
                        rx.el.span(
                            DealState.filtered_deals.length(), class_name="font-medium"
                        ),
                        " deals",
                        class_name="text-sm text-gray-700",
                    ),
                    class_name="hidden sm:flex-1 sm:flex sm:items-center sm:justify-start",
                ),
                rx.el.div(
                    rx.el.button(
                        "Prev",
                        on_click=DealState.prev_page,
                        disabled=DealState.current_page <= 1,
                        class_name="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed mr-2",
                    ),
                    rx.el.button(
                        "Next",
                        on_click=DealState.next_page,
                        disabled=DealState.current_page >= DealState.total_pages,
                        class_name="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    class_name="flex-1 flex justify-end",
                ),
                class_name="bg-white px-6 py-4 border-t border-gray-200 flex items-center justify-between sticky bottom-0",
            ),
            class_name="flex-1 flex flex-col min-w-0 bg-white h-full",
        ),
        alert_sidebar(),
        class_name="flex flex-1 h-[calc(100vh-64px)] overflow-hidden",
    )