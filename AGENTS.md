# Deal Management App Context & Guidelines

## 1. Project Overview
**Name**: Deal Management App
**Type**: Full-stack Web Application
**Framework**: Reflex (Python)
**Purpose**: Manage financial deals, reviews, and alerts.

## 2. Architecture
*   **Split-State Pattern**:
    *   `DealState` (Global): Holds the master list of deals (`self.deals`) and view logic.
    *   `DealFormState` (Transient): Handles form inputs, validation, and temporary state.
    *   **Rule**: Do not mix form state into the global state. Use `get_state(DealFormState)` if needed, but prefer decoupling.
*   **Data Models** (`app/states/schema.py`):
    *   `Deal`: SQLModel-based entity.
    *   `Alert`: SQLModel-based entity.
*   **Validation**:
    *   Currently using `ValidationService` (`app/states/validation.py`).
    *   *Plan*: Migrate to Pydantic validators in `Deal` schema.

## 3. Directory Structure
*   `app/app.py`: Entry point and routing.
*   `app/states/`: Business logic.
*   `app/pages/`: UI Pages.
*   `app/components/`: Reusable UI components.
*   `skills/`: Documentation and guides for tools/skills (e.g., uv).
*   `docs/`: Detailed project documentation.

## 4. Coding Standards (Reflex)
*   **UI Components**:
    *   Use `rx.cond` for conditional rendering, not Python `if/else`.
    *   Use `rx.foreach` for lists.
    *   Style with Tailwind CSS via `class_name` props.
*   **State**:
    *   Variables in `State` classes must be type-hinted.
    *   Use `@rx.var` for computed properties.
    *   Use `@rx.event` for event handlers.
    *   **Async**: Event handlers can be `async` if they perform I/O.
*   **Forms**:
    *   Bind inputs to State vars or use `on_change` handlers.

## 5. Development Workflow
*   **Run Dev Server**: `reflex run`
*   **Install Dependencies**: `pip install -r requirements.txt` (or use `uv`).
*   **Testing**: Run `pytest` (when tests are added).

## 6. Tools & Skills
*   **UV**: This project includes a guide for `uv` in `skills/uv-package-manager/`. Agents should refer to this for dependency management tasks.
*   **MCP**: This repository is designed to be accessible by MCP-compliant agents. Ensure you read `AGENTS.md` and `docs/` before making changes.

## 7. Common Tasks for Agents
*   **Refactoring**: Check `IMPROVEMENTS.md` for current technical debt and goals.
*   **Documentation**: Keep `docs/` updated when changing logic.
*   **Validation**: When adding fields, update `ValidationService` or `Deal` schema.
