import reflex as rx
from app.components.deals.deal_form_component import deal_form_component
from app.states.deals.deals_state import DealState
from app.states.deals.deal_form_state import DealFormState


def upload_tab_button(label: str, tab_value: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: DealState.set_upload_tab(tab_value),
        class_name=rx.cond(
            DealState.upload_tab == tab_value,
            "px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600",
            "px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700",
        ),
    )


def recent_upload_item(
    name: str, meta: str, status: str, icon_color: str
) -> rx.Component:
    status_color = rx.match(
        status,
        ("Processed", "bg-green-100 text-green-800"),
        ("Processing...", "bg-yellow-100 text-yellow-800"),
        ("Failed", "bg-red-100 text-red-800"),
        "bg-gray-100 text-gray-800",
    )
    return rx.el.div(
        rx.icon("file-text", class_name=f"w-8 h-8 {icon_color}"),
        rx.el.div(
            rx.el.p(name, class_name="text-sm font-medium text-gray-900"),
            rx.el.p(meta, class_name="text-xs text-gray-500"),
            class_name="ml-3 flex-1",
        ),
        rx.el.span(
            status,
            class_name=f"inline-flex items-center px-2 py-0.5 rounded text-xs font-medium {status_color}",
        ),
        class_name="flex items-center p-3 bg-white border border-gray-100 rounded-lg mb-2 transition-colors hover:border-blue-100",
    )


def deals_add_view() -> rx.Component:
    """Add deals view content (used inside module layout)."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Ingestion Source", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Upload documentation to extract data automatically.",
                    class_name="text-sm text-gray-500 mt-1",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            upload_tab_button("Upload PDF", "upload"),
                            upload_tab_button("Paste Text", "paste"),
                            class_name="flex border-b border-gray-200 mb-6",
                        ),
                        rx.cond(
                            DealState.upload_tab == "upload",
                            rx.el.div(
                                rx.icon(
                                    "cloud-upload",
                                    class_name="mx-auto h-12 w-12 text-gray-400",
                                ),
                                rx.el.p(
                                    "Click to upload or drag and drop",
                                    class_name="mt-2 text-sm font-medium text-gray-900",
                                ),
                                rx.el.p(
                                    "Supported formats: PDF, DOCX (Term Sheets, Prospectus)",
                                    class_name="mt-1 text-xs text-gray-500",
                                ),
                                rx.el.button(
                                    "Browse Files",
                                    class_name="mt-4 px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50",
                                ),
                                class_name="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors cursor-pointer",
                            ),
                            rx.el.div(
                                rx.el.textarea(
                                    placeholder="Paste deal text or summary here...",
                                    class_name="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm",
                                ),
                                rx.el.button(
                                    "Process Text",
                                    class_name="mt-4 w-full px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700",
                                ),
                            ),
                        ),
                        class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Recent Uploads",
                            class_name="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
                        ),
                        rx.el.div(
                            recent_upload_item(
                                "Global_Tech_Term_Sheet_v2.pdf",
                                "2.4 MB • Uploaded 10 mins ago",
                                "Processed",
                                "text-red-500",
                            ),
                            recent_upload_item(
                                "Project_Titan_Memo.docx",
                                "1.1 MB • Uploaded 1 hr ago",
                                "Processing...",
                                "text-blue-500",
                            ),
                        ),
                        class_name="mt-8",
                    ),
                    class_name="col-span-12 lg:col-span-3",
                ),
                # Main Form Area - 9 columns on desktop (75% width)
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "file-pen-line", class_name="w-4 h-4 text-blue-600 mr-2"
                        ),
                        rx.el.h2(
                            "New Deal Details",
                            class_name="text-base font-semibold text-gray-900",
                        ),
                        class_name="flex items-center mb-4",
                    ),
                    deal_form_component(),
                    class_name="col-span-12 lg:col-span-9",
                ),
                class_name="grid grid-cols-12 gap-4",
            ),
            class_name="w-full px-4 py-6",
        ),
        class_name="min-h-screen bg-gray-50",
        on_mount=DealFormState.on_page_load,
    )
