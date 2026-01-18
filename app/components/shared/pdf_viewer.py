"""
PDF Viewer Component - A shared Reflex component for displaying PDF documents.

This module provides Document and Page components that wrap react-pdf,
enabling PDF viewing capabilities in Reflex applications.

Usage:
    from app.components.shared.pdf_viewer import Document, Page

    Document.create(
        Page.create(page_number=State.current_page, scale=1.2),
        file="/assets/docs/sample.pdf",
        on_load_success=State.load_success,
        loading=rx.text("Loading PDF..."),
    )
"""

import reflex as rx


class Document(rx.NoSSRComponent):
    """
    PDF Document container component.

    Wraps the react-pdf Document component to display PDF files.
    Uses NoSSRComponent since react-pdf requires browser APIs.

    Props:
        file: Path to PDF file, URL, or binary data (str | bytes | dict)
        on_load_success: Callback when PDF loads, receives dict with numPages
        on_load_error: Callback when PDF fails to load
        loading: Component to display while PDF is loading
    """

    library = "react-pdf@9.1.1"
    tag = "Document"

    # Props that map to our React component
    file: rx.Var[str]
    loading: rx.Var[str] | None = None

    # Event handler for when PDF loads successfully
    # react-pdf calls onLoadSuccess with a PDF document proxy object
    # We extract just numPages to avoid circular reference serialization issues
    on_load_success: rx.EventHandler[lambda pdf: [{"numPages": pdf.numPages}]]
    on_load_error: rx.EventHandler[lambda error: [{"message": str(error)}]]

    # Explicitly map snake_case props to camelCase for React
    _rename_props = {
        "on_load_success": "onLoadSuccess",
        "on_load_error": "onLoadError",
    }

    def add_imports(self) -> dict:
        """Import pdfjs for worker configuration."""
        return {
            "react-pdf": ["pdfjs"],
            # Required CSS for proper text layer rendering
            "react-pdf/dist/Page/AnnotationLayer.css": [],
            "react-pdf/dist/Page/TextLayer.css": [],
        }

    def add_hooks(self) -> list[str]:
        """Configure the PDF.js worker using CDN with explicit version."""
        return [
            # React-pdf 9.1.1 uses pdfjs-dist 4.4.168
            'pdfjs.GlobalWorkerOptions.workerSrc = "https://unpkg.com/pdfjs-dist@4.4.168/build/pdf.worker.min.mjs";',
        ]


class Page(rx.NoSSRComponent):
    """
    PDF Page renderer component.

    Wraps the react-pdf Page component to render individual PDF pages.
    Must be used as a child of Document.

    Props:
        page_number: The page number to display (1-indexed)
        scale: Zoom scale factor (default 1.0)
        render_annotation_layer: Whether to render annotations (default True)
        render_text_layer: Whether to render selectable text layer (default True)
    """

    library = "react-pdf@9.1.1"
    tag = "Page"

    page_number: rx.Var[int]
    scale: rx.Var[float] | None = None
    width: rx.Var[int] | None = None
    render_annotation_layer: rx.Var[bool] | None = None
    render_text_layer: rx.Var[bool] | None = None

    _rename_props = {
        "page_number": "pageNumber",
        "render_annotation_layer": "renderAnnotationLayer",
        "render_text_layer": "renderTextLayer",
        "width": "width",
    }


# Convenience function to create a basic PDF viewer with navigation
def pdf_viewer_with_nav(
    file: str,
    current_page: rx.Var[int],
    total_pages: rx.Var[int],
    on_load_success: rx.EventHandler,
    on_prev: rx.EventHandler,
    on_next: rx.EventHandler,
    scale: float = 1.0,
) -> rx.Component:
    """
    Create a PDF viewer with navigation controls.

    Args:
        file: Path to the PDF file
        current_page: State variable for current page number
        total_pages: State variable for total pages
        on_load_success: Handler called when PDF loads
        on_prev: Handler for previous page button
        on_next: Handler for next page button
        scale: Zoom scale factor

    Returns:
        A Reflex component with the PDF viewer and navigation
    """
    return rx.vstack(
        rx.hstack(
            rx.button(
                rx.icon("chevron-left"),
                "Prev",
                on_click=on_prev,
                disabled=current_page <= 1,
                variant="soft",
            ),
            rx.text(
                "Page ",
                rx.text(current_page, as_="span", weight="bold"),
                " of ",
                rx.text(total_pages, as_="span", weight="bold"),
            ),
            rx.button(
                "Next",
                rx.icon("chevron-right"),
                on_click=on_next,
                disabled=current_page >= total_pages,
                variant="soft",
            ),
            spacing="3",
            align="center",
        ),
        Document.create(
            Page.create(
                page_number=current_page,
                scale=scale,
                render_annotation_layer=True,
                render_text_layer=True,
            ),
            file=file,
            on_load_success=on_load_success,
            loading=rx.center(
                rx.text("Loading PDF...", color_scheme="gray"),
                width="100%",
                padding="20px",
            ),
        ),
        spacing="4",
        align="center",
        width="100%",
    )
