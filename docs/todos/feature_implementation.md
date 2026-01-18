# Feature Implementation Gaps

This document tracks features that are currently visible in the User Interface but lack backend implementation or functional logic. These "visual shells" need to be connected to real services.

## 1. Document Ingestion (Add Deal Page)

### 1.1 File Upload
**Location**: `app/pages/deals/add_page.py`
- **UI Element**: "Upload PDF" tab -> "Browse Files" button.
- **Current Behavior**: Button is purely visual. No file picker opens.
- **Missing Implementation**:
  - `rx.upload` component integration.
  - Backend handler to receive file bytes.
  - Storage service (S3/Azure Blob/Local) to save the file.
  - Database record creation in `deals` table (linked to file path).

**Code Reference**:
```python
# app/pages/deals/add_page.py:L81-84
rx.el.button(
    "Browse Files",
    class_name="... cursor-pointer",
)
# Needs conversion to:
# rx.upload(
#     rx.el.button("Browse Files"),
#     id="upload1",
# )
```

### 1.2 Text Paste Ingestion
**Location**: `app/pages/deals/add_page.py`
- **UI Element**: "Paste Text" tab -> Textarea + "Process Text" button.
- **Current Behavior**: "Process Text" button has no `on_click` handler.
- **Missing Implementation**:
  - Event handler `DealAddMixin.process_text(text)`.
  - NLP service connection to extract deal fields (Ticker, Amount, etc.) from raw text.
  - Logic to populate `DealFormState` with extracted values.

**Code Reference**:
```python
# app/pages/deals/add_page.py:L92-95
rx.el.button(
    "Process Text",
    # Missing: on_click=DealAddMixin.process_pasted_text
    class_name="...",
)
```

## 2. Document Review (Review Page)

### 2.1 Document Viewer
**Location**: `app/pages/deals/review_page.py`
- **UI Element**: "Source Document" section -> "Open in Viewer" button.
- **Current Behavior**: Button is inactive.
- **Missing Implementation**:
  - PDF Viewer component (e.g., `react-pdf` wrapper or iframe).
  - Backend endpoint to serve secure file content (`GET /api/documents/{id}`).
  - State logic to toggle viewer modal/panel.

**Code Reference**:
```python
# app/pages/deals/review_page.py:L121-124
rx.el.button(
    "Open in Viewer",
    # Missing: on_click=DealReviewMixin.open_document_viewer
    class_name="...",
)
```

### 2.2 Source File Links
**Location**: `app/pages/deals/review_page.py`
- **UI Element**: Filename link (e.g., "HCIX_term_sheet.pdf").
- **Current Behavior**: Shows a toast "Opening document from secure shared drive...".
- **Missing Implementation**:
  - Actual file download or open action.
  - Secure presigned URL generation if using cloud storage.

**Code Reference**:
```python
# app/pages/deals/review_page.py:L109-116
rx.el.a(
    DealState.active_review_deal.source_file,
    href="#", # Needs real URL
    on_click=rx.toast(...), # Needs real handler
    ...
)
```

## 3. Implementation Priorities

1.  **File Upload**: Prerequisite for any real deal creation workflow.
2.  **File Serving**: Required for the Review page to be useful.
3.  **Text Processing**: High-value feature for efficiency but secondary to basic file storage.
4.  **Integrated Viewer**: Nice-to-have; browser default PDF viewer (via link) is a good interim step.
