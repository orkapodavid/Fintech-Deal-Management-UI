# Feature Pre-Production Implementation Plan

This document outlines "Pre-Production" implementations: functional logic that can be built **now** using local state and simple Python processing, without waiting for the full Database or API layer. These tasks convert "visual shells" into high-fidelity prototypes suitable for demos and user testing.

---

## Implementation Checklist

### Feature 1: Text Ingestion & Parsing
- [ ] Create `app/services/deals/text_parser_service.py`
  - [ ] Define `TextParserService` class
  - [ ] Implement `parse_deal_text(text: str) -> dict` method with regex patterns
  - [ ] Implement `calculate_confidence(extracted: dict) -> int` method
- [ ] Update `app/states/deals/mixins/add_mixin.py`
  - [ ] Add `pasted_text: str = ""` state variable
  - [ ] Add `set_pasted_text(text: str)` event handler
  - [ ] Add `process_pasted_text()` async event handler
- [ ] Update `app/pages/deals/add_page.py`
  - [ ] Connect textarea `on_change` to `DealState.set_pasted_text`
  - [ ] Connect "Process Text" button `on_click` to `DealState.process_pasted_text`
- [ ] Browser test: Paste text → Form auto-populates

### Feature 2: Client-Side File Upload
- [x] Reference: [Reflex Upload Patterns](../.agents/skills/reflex-dev/references/reflex-upload.mdc)
- [x] Create `app/services/deals/file_upload_service.py`
  - [x] Define `FileUploadService` class with `UPLOAD_DIR = Path("./data/uploads/deals")`
  - [x] Implement `validate_file_type(filename: str) -> bool` method
  - [x] Implement `save_uploaded_file(tmp_path: Path, original_name: str) -> dict` method
  - [x] Implement UUID-based unique filename generation
  - [x] Implement `format_file_size(size_bytes: int) -> str` utility
- [x] Update `app/states/deals/mixins/add_mixin.py`
  - [x] Add `uploaded_file: dict = {}` state variable
  - [x] Add `upload_error: str = ""` state variable
  - [x] Add `is_uploading: bool = False` state variable
  - [x] Add `on_file_upload(files: list[dict])` event handler
  - [x] Add `clear_uploaded_file()` event handler
- [x] Update `app/pages/deals/add_page.py`
  - [x] Replace fake button with `rx.upload()` component
  - [x] Add drag-drop zone with styling
  - [x] Display upload progress spinner
  - [x] Show error callout on failure
  - [x] Display uploaded filename badge with remove button
- [ ] Browser test: Drag file → Upload completes → Filename displayed → Clear works

### Feature 3: PDF Viewer (Review Page)
- [x] Reference: [PDF Viewer Implementation Guide](../libraries/pdf_viewer/README.md)
- [x] Update `app/states/deals/mixins/review_mixin.py`
  - [x] Add `n_pages: int = 1` state variable
  - [x] Add `current_pdf_page: int = 1` state variable
  - [x] Add `@rx.var document_path` computed property
  - [x] Add `on_pdf_load_success(info: dict)` event handler
  - [x] Add `pdf_prev_page()` event handler
  - [x] Add `pdf_next_page()` event handler
- [x] Update `app/pages/deals/review_page.py`
  - [x] Import `Document, Page` from `app.components.shared.pdf_viewer`
  - [x] Replace "Open in Viewer" button with embedded PDF viewer component
- [ ] Browser test: Navigate to review page → PDF displays → Navigation works

---

## 1. Text Ingestion & Parsing (Add Deal Page)

### 1.1 Create TextParserService

**File**: `app/services/deals/text_parser_service.py` (NEW)

```python
import re
from typing import Optional
# TODO: Uncomment when integrating OpenAI API
# from openai import OpenAI
# import json

class TextParserService:
    """Service for parsing deal text and extracting structured data.
    
    MOCK IMPLEMENTATION: Uses regex patterns for demo purposes.
    
    TODO: OPENAI API INTEGRATION
    ============================
    To integrate OpenAI API for real AI extraction:
    
    1. Install openai: `uv add openai`
    
    2. Add environment variable: OPENAI_API_KEY
    
    3. Replace parse_deal_text() with:
       async def parse_deal_text_ai(self, text: str) -> dict:
           client = OpenAI()
           response = client.chat.completions.create(
               model="gpt-4o-mini",
               messages=[
                   {"role": "system", "content": self.SYSTEM_PROMPT},
                   {"role": "user", "content": text}
               ],
               response_format={"type": "json_object"}
           )
           return json.loads(response.choices[0].message.content)
    
    4. Add SYSTEM_PROMPT constant (see below)
    """
    
    # TODO: Use this prompt for OpenAI integration
    # SYSTEM_PROMPT = '''
    # Extract deal information from the following text. Return a JSON object with these fields:
    # - ticker: Stock ticker symbol (1-5 uppercase letters)
    # - company_name: Full company name
    # - shares_amount: Number of shares in millions (numeric)
    # - pricing_date: Pricing date (YYYY-MM-DD format)
    # - announce_date: Announcement date (YYYY-MM-DD format)
    # - structure: One of: IPO, M&A, Spin-off, Follow-on, Convertible
    # - sector: Industry sector
    # - country: Country of origin
    # - offering_price: Price per share (numeric)
    # - market_cap: Market capitalization in millions (numeric)
    # 
    # Only include fields that are explicitly mentioned. Use null for missing fields.
    # '''
    
    # MOCK: Regex patterns for fallback/demo extraction
    PATTERNS = {
        "ticker": r"(?:Ticker|Symbol)[:\s]+([A-Z]{1,5})",
        "company_name": r"(?:Company|Issuer|Name)[:\s]+([A-Za-z0-9\s&.,]+?)(?:\n|$)",
        "shares_amount": r"(?:Amount|Shares|Size)[:\s]+\$?([\d,]+(?:\.\d+)?)\s*(?:M|million)?",
        "pricing_date": r"(?:Pricing|Price)\s*(?:Date)?[:\s]+(\d{4}-\d{2}-\d{2})",
        "announce_date": r"(?:Announce|Announced)\s*(?:Date)?[:\s]+(\d{4}-\d{2}-\d{2})",
        "structure": r"(?:Structure|Type|Deal Type)[:\s]+(IPO|M&A|Spin-off|Follow-on|Convertible)",
        "sector": r"(?:Sector|Industry)[:\s]+([A-Za-z]+)",
        "country": r"(?:Country|Region)[:\s]+([A-Za-z]+)",
    }
    
    def parse_deal_text(self, text: str) -> dict:
        """MOCK: Extract deal fields using regex patterns.
        
        TODO: Replace with parse_deal_text_ai() for production.
        """
        extracted = {}
        for field, pattern in self.PATTERNS.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                if field == "shares_amount":
                    value = float(value.replace(",", ""))
                extracted[field] = value
        return extracted
    
    def calculate_confidence(self, extracted: dict) -> int:
        """Calculate confidence score based on fields extracted.
        
        MOCK: Returns 20-100% based on regex matches.
        TODO: For OpenAI, use the model's confidence or token probabilities.
        """
        total_fields = len(self.PATTERNS)
        found_fields = len(extracted)
        # Base 20% + proportional to fields found
        return min(100, int((found_fields / total_fields) * 100) + 20)
```

### 1.2 Update Add Mixin

**File**: `app/states/deals/mixins/add_mixin.py` (MODIFY)

Add new state variables and handlers:
- `pasted_text: str = ""`
- `set_pasted_text(text: str)` event
- `process_pasted_text()` async event that calls TextParserService and updates DealFormState

### 1.3 Update Add Page

**File**: `app/pages/deals/add_page.py` (MODIFY)

Connect UI elements:
- Textarea: `on_change=DealState.set_pasted_text`
- Button: `on_click=DealState.process_pasted_text`

---

## 2. Client-Side File Handling (Add Deal Page)

> **Reference**: [Reflex Upload Patterns](../../.agents/skills/reflex-dev/references/reflex-upload.mdc)

### 2.1 Create FileUploadService

**File**: `app/services/deals/file_upload_service.py` (NEW)

```python
import os
import shutil
from pathlib import Path
from uuid import uuid4

class FileUploadService:
    """Service for handling deal document uploads."""
    
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc"]
    UPLOAD_DIR = Path("./data/uploads/deals")
    
    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    def validate_file_type(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.ALLOWED_EXTENSIONS
    
    def save_uploaded_file(self, tmp_path: Path, original_name: str) -> dict:
        """
        Move file from temp location to custom storage.
        
        Args:
            tmp_path: Temporary file path from Reflex upload
            original_name: Original filename from upload
            
        Returns:
            dict with name, path, size, size_formatted
        """
        filename = os.path.basename(original_name)
        _, ext = os.path.splitext(filename.lower())
        
        # Generate unique filename to prevent collisions
        unique_name = f"{os.path.splitext(filename)[0]}-{uuid4().hex[:8]}{ext}"
        dest = self.UPLOAD_DIR / unique_name
        
        # Move from temp to permanent storage
        shutil.move(str(tmp_path), str(dest))
        file_size = dest.stat().st_size
        
        return {
            "name": filename,
            "unique_name": unique_name,
            "path": str(dest),
            "size": file_size,
            "size_formatted": self.format_file_size(file_size),
        }
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
```

### 2.2 Update Add Mixin

**File**: `app/states/deals/mixins/add_mixin.py` (MODIFY)

Add file upload state and `on_upload` event handler:

```python
from pathlib import Path
from app.services.deals.file_upload_service import FileUploadService

class AddMixin(rx.State):
    # File upload state
    uploaded_file: dict = {}  # {name, path, size_formatted}
    upload_error: str = ""
    is_uploading: bool = False

    @rx.event
    def on_file_upload(self, files: list[dict]):
        """
        Handle file upload from rx.upload component.
        
        Reflex posts files to /_upload route, then calls this handler
        with file metadata including temporary path.
        """
        self.is_uploading = True
        self.upload_error = ""
        
        service = FileUploadService()
        
        for f in files:
            try:
                # Extract temp path and original name from payload
                tmp_path = Path(f.get("path", ""))
                original_name = f.get("name", tmp_path.name)
                
                # Validate file type
                if not service.validate_file_type(original_name):
                    self.upload_error = f"Invalid file type: {original_name}"
                    continue
                
                # Verify temp file exists
                if not tmp_path.exists():
                    self.upload_error = f"Temp file not found"
                    continue
                
                # Save to permanent storage
                self.uploaded_file = service.save_uploaded_file(tmp_path, original_name)
                
            except Exception as e:
                self.upload_error = f"Upload failed: {str(e)}"
        
        self.is_uploading = False

    @rx.event
    def clear_uploaded_file(self):
        """Clear the uploaded file state."""
        self.uploaded_file = {}
        self.upload_error = ""
```

### 2.3 Update Add Page

**File**: `app/pages/deals/add_page.py` (MODIFY)

Replace fake button with `rx.upload()` component:

```python
# Client-side file filter (advisory only - validate server-side)
ACCEPT_FILES = [".pdf", ".docx", ".doc"]

def upload_section() -> rx.Component:
    """File upload section with drag-drop support."""
    return rx.vstack(
        # Upload component
        rx.upload(
            rx.vstack(
                rx.icon("upload", size=32, color="gray"),
                rx.text("Drag and drop or click to browse", color="gray"),
                rx.text("PDF, DOC, DOCX files up to 10MB", size="1", color="gray"),
                align="center",
                spacing="2",
            ),
            accept=ACCEPT_FILES,
            multiple=False,
            on_upload=DealState.on_file_upload,
            border="2px dashed var(--gray-6)",
            border_radius="8px",
            padding="32px",
            width="100%",
            cursor="pointer",
        ),
        
        # Upload progress/status
        rx.cond(
            DealState.is_uploading,
            rx.hstack(rx.spinner(size="2"), rx.text("Uploading..."), spacing="2"),
        ),
        
        # Error display
        rx.cond(
            DealState.upload_error != "",
            rx.callout(DealState.upload_error, icon="alert-triangle", color="red"),
        ),
        
        # Success: Show uploaded file
        rx.cond(
            DealState.uploaded_file,
            rx.hstack(
                rx.icon("file-text", size=20),
                rx.text(DealState.uploaded_file["name"]),
                rx.badge(DealState.uploaded_file["size_formatted"]),
                rx.button(
                    rx.icon("x", size=16),
                    on_click=DealState.clear_uploaded_file,
                    variant="ghost",
                    size="1",
                ),
                spacing="2",
                padding="8px 12px",
                background="var(--gray-2)",
                border_radius="6px",
            ),
        ),
        
        spacing="3",
        width="100%",
    )
```

### 2.4 Security Considerations

| Check | Implementation |
|-------|----------------|
| Extension validation | Server-side in `FileUploadService.validate_file_type()` |
| Filename sanitization | `os.path.basename()` prevents path traversal |
| Unique filenames | UUID suffix prevents collisions |
| Storage location | Outside web-served static directories |

---

## 3. PDF Viewer (Review Page)

> **Reference**: [PDF Viewer Implementation Guide](../libraries/pdf_viewer/README.md)

### 3.1 Create PDF Viewer State Mixin

**File**: `app/states/deals/mixins/review_mixin.py` (MODIFY)

Add PDF viewer state:
```python
# PDF Viewer state
n_pages: int = 1
current_pdf_page: int = 1

@rx.var
def document_path(self) -> str:
    """Return path to the deal's PDF document."""
    return "/data/inputs/deals/sample_deal.pdf"

@rx.event
def on_pdf_load_success(self, info: dict):
    self.n_pages = info.get("numPages", 1)
    self.current_pdf_page = 1

@rx.event
def pdf_prev_page(self):
    self.current_pdf_page = max(1, self.current_pdf_page - 1)

@rx.event
def pdf_next_page(self):
    self.current_pdf_page = min(self.n_pages, self.current_pdf_page + 1)
```

### 3.2 Update Review Page

**File**: `app/pages/deals/review_page.py` (MODIFY)

Use the shared PDF viewer component:
```python
from app.components.shared.pdf_viewer import Document, Page

# In the page layout, replace "Open in Viewer" button with:
rx.vstack(
    rx.hstack(
        rx.button("<", on_click=DealState.pdf_prev_page,
                  disabled=DealState.current_pdf_page <= 1),
        rx.text(f"{DealState.current_pdf_page} / {DealState.n_pages}"),
        rx.button(">", on_click=DealState.pdf_next_page,
                  disabled=DealState.current_pdf_page >= DealState.n_pages),
    ),
    Document.create(
        Page.create(page_number=DealState.current_pdf_page),
        file=DealState.document_path,
        on_load_success=DealState.on_pdf_load_success,
    ),
    align="center",
)
```

**Static Asset**: `data/inputs/deals/sample_deal.pdf` (EXISTS - 2.3MB)

---

## Verification Plan

### Browser Testing (Manual)
1. **Text Parsing** (NOT IMPLEMENTED): Navigate to `/deals/add` → Paste Text tab → Enter sample text → Click Process → Verify fields populated
2. **File Upload** ✅: Navigate to `/deals/add` → Upload PDF tab → Drag file to drop zone → Verify filename badge appears → Click X to clear
3. **PDF Viewer** ✅: Navigate to `/deals/review?id=<id>` → PDF displays in left panel → Use < > buttons to navigate pages

### Sample Test Text
```
Ticker: ACME
Company: Acme Corporation Inc.
Amount: $50,000,000
Pricing Date: 2026-02-15
Announce Date: 2026-02-01
Structure: IPO
Sector: Technology
Country: USA
```

---

## Summary of Work

| Feature | Current State | Pre-Prod Goal | Files Modified | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Text Parsing** | No Handler | Real Regex Parsing | 3 files (1 new service) | ⏳ Pending |
| **File Upload** | Visual Button | **Real File Selection** | 3 files (1 new service) | ✅ Complete |
| **PDF Viewer** | Dead Button | **Embedded PDF Viewer** | 2 files + shared component | ✅ Complete |

### Files Created/Modified

**Feature 2 - File Upload:**
- `app/services/deals/file_upload_service.py` (NEW)
- `app/states/deals/mixins/add_mixin.py` (MODIFIED)
- `app/pages/deals/add_page.py` (MODIFIED)

**Feature 3 - PDF Viewer:**
- `app/components/shared/pdf_viewer.py` (NEW - from earlier task)
- `app/states/deals/mixins/review_mixin.py` (MODIFIED)
- `app/pages/deals/review_page.py` (MODIFIED)

