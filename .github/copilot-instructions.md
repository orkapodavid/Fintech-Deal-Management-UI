# Copilot Instructions

You are an AI assistant helping with a Reflex (Python) web application.

## Project Context
*   **App Name**: Deal Management App
*   **Architecture**: Reflex with Split-State pattern (`DealState` vs `DealFormState`).
*   **Documentation**: See `AGENTS.md` and `docs/` for details.

## Coding Guidelines
1.  **Reflex Components**:
    *   Use `rx` prefix for components (e.g., `rx.text`, `rx.button`).
    *   Prefer `rx.cond` over `if` for reactive UI.
    *   Use `rx.foreach` for lists.
2.  **State**:
    *   Define state vars in classes inheriting from `rx.State`.
    *   Use `@rx.event` for handlers.
    *   Use `@rx.var` for computed props.
3.  **Styling**:
    *   Use Tailwind CSS classes in `class_name`.

## Known Patterns
*   **Forms**: Managed by `DealFormState` using a dictionary `form_values` and explicit validation.
*   **Validation**: Custom `ValidationService` in `app/states/validation.py`.
