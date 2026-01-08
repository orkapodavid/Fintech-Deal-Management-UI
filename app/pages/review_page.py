import reflex as rx
from app.states.deal_state import DealState
from app.components.deal_form_component import deal_form_component


def queue_row(deal: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.icon("clock", class_name="text-amber-500 w-5 h-5"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.a(
                deal.ticker,
                href=rx.Var.create(f"/review?id={deal.id}"),
                class_name="font-semibold text-blue-600 hover:underline cursor-pointer",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-900",
        ),
        rx.el.td(
            deal.created_at.to_string(),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-500",
        ),
        rx.el.td(
            rx.el.span(
                f"{deal.ai_confidence_score}%",
                class_name=rx.cond(
                    deal.ai_confidence_score >= 60,
                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
                    rx.cond(
                        deal.ai_confidence_score >= 40,
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800",
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800",
                    ),
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon("file-text", class_name="w-4 h-4 text-gray-400 mr-2"),
                rx.el.a(
                    deal.source_file,
                    href="#",
                    on_click=rx.toast(
                        "Opening document from secure shared drive...", duration=2000
                    ),
                    class_name="text-sm text-blue-600 hover:text-blue-800 hover:underline truncate max-w-[150px]",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.a(
                    "Review",
                    href=rx.Var.create(f"/review?id={deal.id}"),
                    class_name="text-blue-600 hover:text-blue-900 text-sm font-medium",
                ),
                class_name="flex space-x-3",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="bg-white border-b hover:bg-gray-50 transition-colors",
    )


def review_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                DealState.active_review_deal,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.h3(
                                        "Source Document",
                                        class_name="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            rx.icon(
                                                "file-text",
                                                class_name="w-12 h-12 text-gray-300 mb-2",
                                            ),
                                            rx.el.a(
                                                DealState.active_review_deal.source_file,
                                                href="#",
                                                on_click=rx.toast(
                                                    "Opening document from secure shared drive...",
                                                    duration=2000,
                                                ),
                                                class_name="text-sm font-medium text-blue-600 hover:underline hover:text-blue-800 mb-2",
                                            ),
                                            rx.el.p(
                                                "Extracted content visualization available",
                                                class_name="text-xs text-gray-500 text-center",
                                            ),
                                            rx.el.button(
                                                "Open in Viewer",
                                                class_name="mt-4 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50",
                                            ),
                                            class_name="flex flex-col items-center justify-center h-full",
                                        ),
                                        class_name="w-full h-[calc(100%-40px)] rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 p-4",
                                    ),
                                    class_name="w-1/3 h-full p-6 border-r border-gray-200 hidden xl:block",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.div(
                                            rx.el.h2(
                                                f"Reviewing: {DealState.active_review_deal.ticker}",
                                                class_name="text-xl font-bold text-gray-900",
                                            ),
                                            rx.el.div(
                                                rx.el.span(
                                                    "Confidence Score: ",
                                                    class_name="text-sm text-gray-500 mr-2",
                                                ),
                                                rx.el.span(
                                                    f"{DealState.active_review_deal.ai_confidence_score}%",
                                                    class_name="text-lg font-bold text-gray-900",
                                                ),
                                                rx.cond(
                                                    DealState.active_review_deal.ai_confidence_score
                                                    < 60,
                                                    rx.el.span(
                                                        "LOW CONFIDENCE",
                                                        class_name="ml-3 inline-flex items-center px-2.5 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-800 animate-pulse",
                                                    ),
                                                    None,
                                                ),
                                                class_name="flex items-center",
                                            ),
                                            class_name="flex items-center justify-between mb-6 pb-4 border-b border-gray-100",
                                        ),
                                        deal_form_component(),
                                        class_name="w-full",
                                    ),
                                    class_name="flex-1 h-full overflow-y-auto p-6 bg-white",
                                ),
                                class_name="flex h-full",
                            ),
                            class_name="h-full",
                        ),
                        class_name="h-full",
                    ),
                    class_name="h-full",
                ),
                rx.el.div(
                    rx.icon("file-search", class_name="w-16 h-16 text-gray-300 mb-4"),
                    rx.el.h3(
                        "Ready for Review",
                        class_name="text-lg font-medium text-gray-900",
                    ),
                    rx.el.p(
                        "Select a pending deal from the queue below to start AI validation.",
                        class_name="text-gray-500 mt-2",
                    ),
                    class_name="flex flex-col items-center justify-center h-full bg-gray-50",
                ),
            ),
            class_name="h-[60vh] border-b border-gray-200 bg-white shadow-sm z-10 relative",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Pending Review Queue",
                        class_name="text-sm font-bold text-gray-900 uppercase tracking-wider",
                    ),
                    rx.el.span(
                        f"{DealState.pending_deals.length()} items",
                        class_name="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full",
                    ),
                    class_name="flex items-center px-6 py-3 bg-gray-50 border-b border-gray-200 sticky top-0 z-10",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Status",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Ticker",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Ingest Time",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Confidence",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Source File",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Actions",
                                    class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                ),
                                class_name="bg-gray-50 border-b border-gray-200",
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(DealState.pending_deals, queue_row),
                            class_name="bg-white divide-y divide-gray-200",
                        ),
                        class_name="min-w-full divide-y divide-gray-200",
                    ),
                    class_name="overflow-x-auto",
                ),
                class_name="h-full overflow-y-auto",
            ),
            class_name="h-[40vh] bg-white",
        ),
        class_name="flex flex-col h-[calc(100vh-64px)] overflow-hidden",
    )