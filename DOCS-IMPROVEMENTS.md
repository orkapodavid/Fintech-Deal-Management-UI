# Documentation Improvement Suggestions

Since the `docs/` folder is currently **missing**, the primary goal is to establish a documentation foundation.

## 1. Create a `README.md` (Root)
*   **Action**: Create a root `README.md` acting as the entry point.
*   **Content**: Project title, one-sentence description, quick start command (`reflex run`), and links to detailed docs (setup, architecture).

## 2. Create `docs/` Directory
*   **Action**: Initialize a `docs/` folder to house detailed guides.
*   **Content**:
    *   `docs/setup.md` (Content from `SETUP.md`)
    *   `docs/architecture.md` (Content from `ARCHITECTURE.md`)
    *   `docs/contributing.md`: Guidelines for PRs, code style (Black/Ruff), and testing.

## 3. Document State Patterns
*   **Action**: Explicitly document the "Split State" pattern used here (`DealState` vs `DealFormState`).
*   **Why**: This is a specific architectural choice in this repo. New developers might try to put everything in one state.
*   **Section**: Add to `docs/architecture.md`.

## 4. Add API/Schema Documentation
*   **Action**: specific documentation for the `Deal` object fields and their validation rules.
*   **Why**: Financial domains have complex rules (e.g., "Pricing Date" must be after "Announce Date"). These business rules should be documented for non-technical stakeholders or QA.
