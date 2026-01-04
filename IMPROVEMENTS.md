# Improvements & Refactoring Plan

## 1. Implement Persistent Storage
*   **What**: Replace the in-memory `self.deals` list in `DealState` with actual database queries using `SQLModel` with a SQLite or PostgreSQL backend.
*   **Why**: Currently, all data is lost on server restart. Reflex supports `rx.Model` (SQLModel) natively.
*   **Where**: `app/states/deal_state.py` (replace list operations with `session.add`, `session.exec`), `rxconfig.py` (database config).

## 2. Refactor Validation to Pydantic
*   **What**: Move validation logic from `ValidationService` (`app/states/validation.py`) directly into the `Deal` model in `app/states/schema.py` using Pydantic's `@validator` or `root_validator`.
*   **Why**: Reduces boilerplate. `ValidationService` manually re-implements checks that Pydantic handles natively. It centralizes logic in the Schema.
*   **Where**: `app/states/schema.py`, remove `app/states/validation.py`.

## 3. Clean Up Dependencies & Dead Code
*   **What**:
    *   Remove `PyGithub` from `requirements.txt` (unused).
    *   Delete or refactor `app/components/deal_form.py` if it is indeed superseded by `deal_form_component.py` (checks indicate `deal_form_component.py` is the one in use).
*   **Why**: Reduces build size and confusion for new developers.
*   **Where**: `requirements.txt`, `app/components/deal_form.py`.

## 4. Decouple Form Component
*   **What**: `deal_form_component.py` is hardcoded to use `DealFormState`. Pass state or handlers as props (or use a more generic pattern) to make the component reusable or easier to test.
*   **Why**: Tight coupling makes unit testing the component in isolation difficult and limits reusability.
*   **Where**: `app/components/deal_form_component.py`.

## 5. Add Testing Strategy
*   **What**: Create a `tests/` directory. Add unit tests for `ValidationService` (or the new Pydantic models) and state logic (`DealState`).
*   **Why**: Critical for financial applications to ensure data integrity and logic correctness.
*   **Where**: New folder `tests/`.
