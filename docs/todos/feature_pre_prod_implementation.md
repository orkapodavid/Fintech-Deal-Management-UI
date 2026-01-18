# Feature Pre-Production Implementation Plan

This document outlines "Pre-Production" implementations: functional logic that can be built **now** using local state and simple Python processing, without waiting for the full Database or API layer. These tasks convert "visual shells" into high-fidelity prototypes suitable for demos and user testing.

---

## 1. Text Ingestion & Parsing (Add Deal Page)

Make the "Paste Text" feature actually work by implementing a local rule-based parser. This demonstrates the "AI Extraction" value proposition immediately.

### 1.1 Implement `process_pasted_text` Handler
*   **Goal**: auto-populate form fields when user clicks "Process Text".
*   **Logic**:
    *   Create a simple regex parser in `app/states/deals/mixins/add_mixin.py`.
    *   Extract key patterns:
        *   Ticker (e.g., `Ticker: \w+`)
        *   Amount (e.g., `Amount: \$?[\d,]+`)
        *   Dates (e.g., `Pricing: \d{4}-\d{2}-\d{2}`)
    *   Update `DealFormState` values with findings.
    *   Update `ai_confidence_score` based on how many fields were found.
*   **User Value**: User pastes text -> Form magically fills up.

## 2. Client-Side File Handling (Add Deal Page)

Replace the fake "Browse Files" button with a working Reflex upload component to handle the file selection state, even if we don't persistently store it yet.

### 2.1 Integrate `rx.upload`
*   **Goal**: Allow user to actually select a file and see it recognized.
*   **Implementation**:
    *   Replace `rx.el.button("Browse Files")` with `rx.upload()`.
    *   Add `on_change` event to capture filename and size.
*   **State Update**:
    *   Display the *actual* selected filename in the UI (replacing the hardcoded "Click to upload..." text or adding a "Selected: filename.pdf" badge).
    *   Enable the "Submit" button only after file selection (if required).

## 3. Mock Viewers & Navigation (Review Page)

Make the Review flow navigation functional using static assets.

### 3.1 Static Asset Viewer
*   **Goal**: "Open in Viewer" should display the document from a dynamic path.
*   **Implementation**:
    *   Update the state to include a `document_path` variable. (i.e. "data\inputs\deals\sample_deal.pdf")
    *   Update "Open in Viewer" button to use `rx.el.a(href=State.document_path, target="_blank")`.
*   **User Value**: Demonstrates the full review window workflow without needing a dynamic document server.

---

## Summary of Work

| Feature | Current State | Pre-Prod Goal | Difficulty |
| :--- | :--- | :--- | :--- |
| **Text Parsing** | No Handler | **Real Regex Parsing** | Low |
| **File Upload** | Visual Button | **Real File Selection** | Low |
| **Viewer** | Dead Button | **Static Sample PDF** | Very Low |
