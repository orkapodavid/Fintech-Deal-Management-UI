import reflex as rx
from app.states.deals.deals_state import DealState
from app.components.deals.deal_form_component import deal_form_component
from app.components.shared.pdf_viewer import Document, Page


def format_ingest_time(timestamp: rx.Var) -> rx.Var:
    """Format ISO timestamp for the review queue.

    Takes ISO string like '2026-01-14T23:10:25.123456' and returns 'MM-DD HH:MM'
    ISO positions: 0123456789012345
                   2026-01-14T23:10:25
    Position 5-10: '01-14' (MM-DD, but includes the dash before as well)
    Position 11-16: 'T23:1' (includes T, missing last digit)

    Correct: 5-10 for MM-DD, 11-16 for T + HH:M, we need to adjust
    Actually: Let's just show full date-time but replace T with space
    """
    # Replace 'T' with ' ' and take chars to get MM-DD HH:MM
    # Adjusted from [5:16] to [6:17] to compensate for Reflex string indexing
    return timestamp.to_string().replace("T", " ")[6:17]


def queue_row(deal: rx.Var) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.icon("clock", class_name="text-amber-500 w-5 h-5"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.a(
                deal.ticker,
                # Use href for client-side routing
                href=rx.Var.create(f"/deals/review?id={deal.id}"),
                class_name="font-semibold text-blue-600 hover:underline cursor-pointer",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-gray-900",
        ),
        rx.el.td(
            format_ingest_time(deal.created_at),
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
                    href=rx.Var.create(f"/deals/review?id={deal.id}"),
                    class_name="text-blue-600 hover:text-blue-900 text-sm font-medium",
                ),
                class_name="flex space-x-3",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
        class_name="bg-white border-b hover:bg-gray-50 transition-colors",
    )


def deals_review_view() -> rx.Component:
    """Review deals view content (used inside module layout)."""
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
                                        class_name="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2",
                                    ),
                                    # File path display
                                    rx.el.div(
                                        rx.icon(
                                            "file-text",
                                            class_name="w-3 h-3 text-gray-400 flex-shrink-0",
                                        ),
                                        rx.el.span(
                                            DealState.document_display_path,
                                            class_name="text-xs text-gray-500 truncate",
                                            title=DealState.document_display_path,
                                        ),
                                        rx.el.button(
                                            rx.icon("copy", class_name="w-3 h-3"),
                                            on_click=rx.set_clipboard(
                                                DealState.document_display_path
                                            ),
                                            class_name="p-0.5 hover:bg-gray-100 rounded text-gray-400 hover:text-gray-600 flex-shrink-0",
                                            title="Copy path to clipboard",
                                        ),
                                        class_name="flex items-center gap-1.5 mb-4 max-w-full overflow-hidden",
                                    ),
                                    # PDF Viewer with Toolbar
                                    rx.el.div(
                                        # Toolbar
                                        rx.el.div(
                                            # Pagination
                                            rx.el.div(
                                                rx.el.button(
                                                    rx.icon(
                                                        "chevron-left",
                                                        class_name="w-4 h-4",
                                                    ),
                                                    on_click=DealState.pdf_prev_page,
                                                    disabled=DealState.current_pdf_page
                                                    <= 1,
                                                    class_name="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-600",
                                                    title="Previous Page",
                                                ),
                                                rx.el.span(
                                                    f"{DealState.current_pdf_page} / {DealState.n_pages}",
                                                    class_name="text-xs font-medium text-gray-600",
                                                ),
                                                rx.el.button(
                                                    rx.icon(
                                                        "chevron-right",
                                                        class_name="w-4 h-4",
                                                    ),
                                                    on_click=DealState.pdf_next_page,
                                                    disabled=DealState.current_pdf_page
                                                    >= DealState.n_pages,
                                                    class_name="p-1 rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed text-gray-600",
                                                    title="Next Page",
                                                ),
                                                class_name="flex items-center space-x-2 border-r border-gray-200 pr-3 mr-3",
                                            ),
                                            # Zoom Controls
                                            rx.el.div(
                                                rx.el.button(
                                                    rx.icon(
                                                        "minus", class_name="w-4 h-4"
                                                    ),
                                                    on_click=DealState.pdf_zoom_out,
                                                    class_name="p-1 rounded hover:bg-gray-100 text-gray-600",
                                                    title="Zoom Out",
                                                ),
                                                rx.el.span(
                                                    rx.cond(
                                                        DealState.pdf_fit_width,
                                                        "Fit",
                                                        f"{DealState.pdf_scale * 100}%",
                                                    ),
                                                    class_name="text-xs font-medium text-gray-600 min-w-[3rem] text-center",
                                                ),
                                                rx.el.button(
                                                    rx.icon(
                                                        "plus", class_name="w-4 h-4"
                                                    ),
                                                    on_click=DealState.pdf_zoom_in,
                                                    class_name="p-1 rounded hover:bg-gray-100 text-gray-600",
                                                    title="Zoom In",
                                                ),
                                                rx.el.button(
                                                    rx.icon(
                                                        "refresh-ccw",
                                                        class_name="w-3 h-3",
                                                    ),
                                                    on_click=DealState.pdf_zoom_reset,
                                                    class_name="p-1 rounded hover:bg-gray-100 text-gray-600 ml-1",
                                                    title="Reset Zoom",
                                                ),
                                                class_name="flex items-center space-x-1 border-r border-gray-200 pr-3 mr-3",
                                            ),
                                            # View Modes
                                            rx.el.div(
                                                rx.el.button(
                                                    rx.icon(
                                                        rx.cond(
                                                            DealState.pdf_fit_width,
                                                            "minimize-2",
                                                            "maximize-2",
                                                        ),
                                                        class_name="w-4 h-4",
                                                    ),
                                                    on_click=DealState.pdf_toggle_fit_width,
                                                    class_name=rx.cond(
                                                        DealState.pdf_fit_width,
                                                        "p-1 rounded bg-blue-50 text-blue-600",
                                                        "p-1 rounded hover:bg-gray-100 text-gray-600",
                                                    ),
                                                    title="Toggle Fit Width",
                                                ),
                                                class_name="flex items-center",
                                            ),
                                            # Spacer to push action buttons to the right
                                            rx.el.div(class_name="flex-grow"),
                                            # Action Buttons (Download, Open Local)
                                            rx.el.div(
                                                # Download button
                                                rx.el.a(
                                                    rx.icon(
                                                        "download", class_name="w-4 h-4"
                                                    ),
                                                    href=DealState.document_path,
                                                    download=True,
                                                    class_name="p-1 rounded hover:bg-gray-100 text-gray-600 inline-flex items-center",
                                                    title="Download PDF",
                                                ),
                                                # Open Local button (only show if network path)
                                                rx.cond(
                                                    DealState.has_network_path,
                                                    rx.el.button(
                                                        rx.icon(
                                                            "external-link",
                                                            class_name="w-4 h-4",
                                                        ),
                                                        on_click=DealState.open_pdf_local,
                                                        class_name="p-1 rounded hover:bg-gray-100 text-gray-600",
                                                        title="Open in system viewer",
                                                    ),
                                                    rx.fragment(),
                                                ),
                                                class_name="flex items-center space-x-1",
                                            ),
                                            class_name="flex items-center p-2 border-b border-gray-200 bg-gray-50",
                                        ),
                                        # PDF Document container
                                        rx.el.div(
                                            Document.create(
                                                Page.create(
                                                    page_number=DealState.current_pdf_page,
                                                    # Use computed effective scale - handles both manual and fit-width modes
                                                    scale=DealState.pdf_effective_scale,
                                                    render_annotation_layer=True,
                                                    render_text_layer=True,
                                                ),
                                                file=DealState.document_path,
                                                on_load_success=DealState.on_pdf_load_success,
                                                on_load_error=DealState.on_pdf_load_error,
                                                loading=rx.el.div(
                                                    rx.el.p(
                                                        "Loading PDF...",
                                                        class_name="text-sm text-gray-500 font-medium",
                                                    ),
                                                    class_name="flex items-center justify-center p-8",
                                                ),
                                            ),
                                            id="pdf-wrapper",
                                            class_name="flex justify-center overflow-auto h-full p-4 bg-gray-100",
                                        ),
                                        class_name="w-full h-[calc(100%-40px)] rounded-xl border border-gray-200 bg-white overflow-hidden flex flex-col",
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
