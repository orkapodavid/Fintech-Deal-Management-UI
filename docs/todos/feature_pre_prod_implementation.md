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
- [ ] Create `app/services/deals/file_upload_service.py`
  - [ ] Define `FileUploadService` class
  - [ ] Implement `validate_file_type(filename: str) -> bool` method
  - [ ] Implement `save_uploaded_file(file: rx.UploadFile) -> dict` async method
  - [ ] Implement `format_file_size(size_bytes: int) -> str` utility
- [ ] Update `app/states/deals/mixins/add_mixin.py`
  - [ ] Add `selected_file: dict = {}` state variable
  - [ ] Add `is_uploading: bool = False` state variable
  - [ ] Add `upload_progress: str = ""` state variable
  - [ ] Add `handle_file_upload(files: list[rx.UploadFile])` async handler
  - [ ] Add `clear_selected_file()` event handler
- [ ] Update `app/pages/deals/add_page.py`
  - [ ] Replace `rx.el.button("Browse Files")` with `rx.upload()` component
  - [ ] Add "Upload Selected File" trigger button
  - [ ] Display selected filename badge when file exists
  - [ ] Show upload progress indicator
- [ ] Browser test: Select file → Filename displayed → Upload works

### Feature 3: Static PDF Viewer
- [ ] Update `app/states/deals/mixins/add_mixin.py`
  - [ ] Add `@rx.var document_path` computed property
- [ ] Update `app/pages/deals/review_page.py`
  - [ ] Update "Open in Viewer" button to `rx.el.a(href=..., target="_blank")`
- [ ] Browser test: Click "Open in Viewer" → PDF opens in new tab

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

### 2.1 Create FileUploadService

**File**: `app/services/deals/file_upload_service.py` (NEW)

```python
import reflex as rx
from pathlib import Path
from typing import Optional

class FileUploadService:
    """Service for handling file uploads."""
    
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc"]
    UPLOAD_DIR = Path("./uploads")
    
    def __init__(self):
        self.UPLOAD_DIR.mkdir(exist_ok=True)
    
    def validate_file_type(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        ext = Path(filename).suffix.lower()
        return ext in self.ALLOWED_EXTENSIONS
    
    async def save_uploaded_file(self, file: rx.UploadFile) -> dict:
        """Save uploaded file and return metadata."""
        upload_data = await file.read()
        file_size = len(upload_data)
        outfile = self.UPLOAD_DIR / file.filename
        
        with open(outfile, "wb") as f:
            f.write(upload_data)
        
        return {
            "name": file.filename,
            "size": file_size,
            "path": str(outfile),
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

Add file upload state and handlers.

### 2.3 Update Add Page

**File**: `app/pages/deals/add_page.py` (MODIFY)

Replace fake button with `rx.upload()` component following the pattern in `.agents/skills/reflex-dev/examples/file_upload.py`.

---

## 3. Static PDF Viewer (Review Page)

### 3.1 Update Review Page

**File**: `app/pages/deals/review_page.py` (MODIFY)

Update "Open in Viewer" button:
```python
rx.el.a(
    "Open in Viewer",
    href="/data/inputs/deals/sample_deal.pdf",
    target="_blank",
    class_name="mt-4 px-3 py-1.5 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50",
)
```

**Static Asset**: `data/inputs/deals/sample_deal.pdf` (EXISTS - 2.3MB)

---

## Verification Plan

### Browser Testing (Automated)
1. **Text Parsing**: Navigate to `/deals/add` → Paste Text tab → Enter sample text → Click Process → Verify fields populated
2. **File Upload**: Navigate to `/deals/add` → Upload PDF tab → Select file → Verify filename shown → Upload → Verify success
3. **PDF Viewer**: Navigate to `/deals/review?id=<id>` → Click "Open in Viewer" → Verify PDF opens

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

| Feature | Current State | Pre-Prod Goal | Files Modified | Difficulty |
| :--- | :--- | :--- | :--- | :--- |
| **Text Parsing** | No Handler | **Real Regex Parsing** | 3 files (1 new service) | Low |
| **File Upload** | Visual Button | **Real File Selection** | 3 files (1 new service) | Low |
| **Viewer** | Dead Button | **Static Sample PDF** | 1 file | Very Low |
