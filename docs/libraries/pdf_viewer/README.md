# PDF Viewer Component Implementation Guide

This guide documents how to implement and use the PDF viewer component that wraps `react-pdf` directly in Reflex without installing the `reflex-pdf-viewer` Python package.

## Overview

The implementation uses Reflex's custom component pattern to directly wrap the `react-pdf` NPM package, providing:
- `Document` - Container component that loads and manages PDF files
- `Page` - Renders individual PDF pages with optional annotations/text layers

## Implementation

### Component Location

```
app/components/shared/pdf_viewer.py
```

### Core Implementation

```python
import reflex as rx


class Document(rx.NoSSRComponent):
    """PDF Document container - wraps react-pdf Document."""

    library = "react-pdf@9.1.1"
    tag = "Document"

    file: rx.Var[str]
    loading: rx.Var[str] | None = None
    on_load_success: rx.EventHandler[lambda info: [info]]

    def add_imports(self) -> dict:
        return {
            "react-pdf": ["pdfjs"],
            "react-pdf/dist/Page/AnnotationLayer.css": [],
            "react-pdf/dist/Page/TextLayer.css": [],
        }

    def add_hooks(self) -> list[str]:
        return [
            'pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;',
        ]


class Page(rx.NoSSRComponent):
    """PDF Page renderer - wraps react-pdf Page."""

    library = "react-pdf@9.1.1"
    tag = "Page"

    page_number: rx.Var[int]
    scale: rx.Var[float] | None = None
    render_annotation_layer: rx.Var[bool] | None = None
    render_text_layer: rx.Var[bool] | None = None

    def _rename_props(self) -> dict[str, str]:
        return {
            "page_number": "pageNumber",
            "render_annotation_layer": "renderAnnotationLayer",
            "render_text_layer": "renderTextLayer",
        }
```

### Configuration

Add `react-pdf` to `rxconfig.py`:

```python
import reflex as rx

config = rx.Config(
    app_name="app",
    frontend_packages=[
        "react-pdf@9.1.1",
    ],
)
```

---

## Usage Example

### Basic Usage with State

```python
import reflex as rx
from app.components.shared.pdf_viewer import Document, Page


class PdfViewerState(rx.State):
    n_pages: int = 1
    current_page: int = 1

    @rx.event
    def load_success(self, info: dict):
        self.n_pages = info.get("numPages", 1)
        self.current_page = 1

    @rx.event
    def prev_page(self):
        self.current_page = max(1, self.current_page - 1)

    @rx.event
    def next_page(self):
        self.current_page = min(self.n_pages, self.current_page + 1)


def pdf_viewer_page() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.button("<", on_click=PdfViewerState.prev_page, 
                      disabled=PdfViewerState.current_page <= 1),
            rx.text(f"{PdfViewerState.current_page} / {PdfViewerState.n_pages}"),
            rx.button(">", on_click=PdfViewerState.next_page,
                      disabled=PdfViewerState.current_page >= PdfViewerState.n_pages),
        ),
        Document.create(
            Page.create(page_number=PdfViewerState.current_page),
            file="/assets/docs/sample.pdf",
            on_load_success=PdfViewerState.load_success,
        ),
        align="center",
    )
```

---

## Component API Reference

### Document

| Prop | Type | Description |
|------|------|-------------|
| `file` | `str` | Path to PDF file (local `/assets/...` or URL) |
| `loading` | `str \| Component` | Content shown while PDF loads |
| `on_load_success` | `EventHandler` | Callback with `{numPages: int}` |

### Page

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `page_number` | `int` | Required | 1-indexed page number |
| `scale` | `float` | `1.0` | Zoom scale factor |
| `render_annotation_layer` | `bool` | `True` | Show PDF annotations |
| `render_text_layer` | `bool` | `True` | Enable text selection |

---

## Key Implementation Details

| Aspect | Implementation |
|--------|----------------|
| Base class | `rx.NoSSRComponent` (browser APIs required) |
| Worker | CDN-loaded via `add_hooks()` |
| CSS | Auto-imported via `add_imports()` |
| Prop conversion | `_rename_props()` for camelCase |

## PDF File Sources

- **Local**: Place in `assets/` folder, reference as `/assets/docs/file.pdf`
- **Remote URL**: Use full URL (CORS must be enabled)
- **Dynamic**: Pass URL from state variable

---

## Related Files

- [pdf_viewer.py](../../../app/components/shared/pdf_viewer.py) - Component implementation

