import reflex as rx
from app.states.deal_state import DealState
from app.components.alert_sidebar import alert_sidebar
from app.components.confirmation_dialog import confirmation_dialog


def sortable_header(label: str, column: str, align: str = "left") -> rx.Component:
    return rx.el.th(
        rx.el.div(
            label,
            rx.cond(
                DealState.sort_column == column,
                rx.cond(
                    DealState.sort_direction == "asc",
                    rx.icon("chevron-up", size=16, class_name="ml-1 text-blue-600"),
                    rx.icon("chevron-down", size=16, class_name="ml-1 text-blue-600"),
                ),
                rx.icon(
                    "arrow-up-down",
                    size=16,
                    class_name="ml-1 text-gray-300 opacity-50 group-hover:opacity-100",
                ),
            ),
            class_name=f"flex items-center gap-1 cursor-pointer group hover:text-gray-700 {('justify-end' if align == 'right' else '')}",
        ),
        on_click=lambda: DealState.sort_by_column(column),
        class_name=f"px-3 py-3 text-{align} text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50 select-none hover:bg-gray-100 transition-colors",
    )


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
                    rx.el.div(
                        rx.icon("search", size=16, class_name="text-gray-400 mr-2"),
                        rx.el.input(
                            placeholder="Search deals...",
                            on_change=DealState.set_search_query.debounce(300),
                            class_name="border-none focus:ring-0 text-sm w-48 p-0 text-gray-700 placeholder:text-gray-400",
                            default_value=DealState.search_query,
                        ),
                        class_name="flex items-center bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 mr-4",
                    ),
                    rx.el.select(
                        rx.el.option("All Status", value="all"),
                        rx.el.option("Active", value="active"),
                        rx.el.option("Pending Review", value="pending_review"),
                        rx.el.option("Draft", value="draft"),
                        value=DealState.filter_status,
                        on_change=DealState.set_filter_status,
                        class_name="block w-32 rounded-md border-gray-300 py-1.5 text-sm focus:border-blue-500 focus:ring-blue-500 mr-2 bg-white shadow-sm cursor-pointer appearance-none",
                    ),
                    rx.el.input(
                        type="date",
                        on_change=DealState.set_filter_start_date,
                        class_name="block rounded-md border-gray-300 py-1.5 text-sm focus:border-blue-500 focus:ring-blue-500 mr-2 shadow-sm text-gray-600",
                        default_value=DealState.filter_start_date,
                    ),
                    rx.el.span("-", class_name="text-gray-400 mx-1"),
                    rx.el.input(
                        type="date",
                        on_change=DealState.set_filter_end_date,
                        class_name="block rounded-md border-gray-300 py-1.5 text-sm focus:border-blue-500 focus:ring-blue-500 mr-4 shadow-sm text-gray-600",
                        default_value=DealState.filter_end_date,
                    ),
                    rx.el.button(
                        "Clear",
                        on_click=DealState.clear_filters,
                        class_name="text-sm text-gray-500 hover:text-gray-700 underline decoration-gray-400",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("download", size=16, class_name="mr-2"),
                        "Export",
                        on_click=DealState.export_deals,
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 mr-4 transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("pencil", size=16, class_name="mr-2"),
                        "Edit Selected",
                        on_click=DealState.edit_selected_deal,
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 mr-4 transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", size=16, class_name="mr-2"),
                        "Delete",
                        on_click=DealState.request_delete,
                        class_name="inline-flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md transition-colors",
                    ),
                    confirmation_dialog(
                        DealState.show_delete_dialog,
                        "Delete Deals",
                        "Are you sure you want to delete the selected deals? This action cannot be undone.",
                        DealState.confirm_delete,
                        DealState.cancel_delete,
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
                            sortable_header("Ticker", "ticker"),
                            sortable_header("Structure", "structure"),
                            rx.el.th(
                                "Flags",
                                class_name="px-3 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider bg-gray-50",
                            ),
                            sortable_header("Shares (M)", "shares_amount", "right"),
                            sortable_header("Offer Price", "offering_price", "right"),
                            sortable_header("Pricing Date", "pricing_date", "right"),
                            sortable_header("Announce Date", "announce_date", "right"),
                            sortable_header("Sector", "sector"),
                            sortable_header("Country", "country"),
                            sortable_header("Mkt Cap (M)", "market_cap", "right"),
                            sortable_header("Conf.", "ai_confidence_score", "center"),
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
                                            deal.id
                                        ),
                                        on_change=lambda _: DealState.toggle_select_deal(
                                            deal.id
                                        ),
                                        class_name="rounded border-gray-300 text-blue-600 focus:ring-blue-500 h-4 w-4",
                                    ),
                                    class_name="pl-6 pr-3 py-4 whitespace-nowrap w-10",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        deal.ticker,
                                        on_click=lambda: DealState.select_deal_for_review(
                                            deal.id
                                        ),
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
                                    rx.el.span(deal.pricing_date),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono",
                                ),
                                rx.el.td(
                                    rx.el.span(deal.announce_date),
                                    class_name="px-3 py-4 whitespace-nowrap text-sm text-gray-500 text-right font-mono",
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