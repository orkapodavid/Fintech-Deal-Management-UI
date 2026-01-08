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

## 8. Lessons Learned

### 8.1 Edit vs Add Mode: Use URL Query Params with Deal ID
**Problem**: Relying on session state (`form_mode`) to distinguish edit vs add mode fails on page refresh—state persists incorrectly. Additionally, using `ticker` as identifier is not reliable since multiple deals can have the same ticker.

**Solution**: Use URL query params with unique deal `id` (e.g., `/add?mode=edit&id=UUID` or `/review?id=UUID`) and check `self.router.page.params.get("id")` in `on_mount` handler. Reset form when not in edit mode.

```python
@rx.event
def on_page_load(self):
    mode = self.router.page.params.get("mode", "add")
    if mode != "edit":
        self.reset_form()
```

### 8.2 Use UUIDs for Entity Identification, Not Business Keys
**Problem**: Using `ticker` as the primary identifier for deals caused issues because:
1. Multiple deals can have the same ticker (e.g., different deal types for the same company)
2. URL parameters like `/review?ticker=AAPL` become ambiguous
3. Selection, deletion, and export operations fail when multiple deals share a ticker

**Solution**: Add a unique `id` field (UUID) to the `Deal` model and use it for all identification:

```python
# schema.py
from pydantic import Field
import uuid

class Deal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticker: str  # Business key, not unique
    # ...
```

**Where to use `id` vs `ticker`:**
| Use Case | Use `id` | Use `ticker` |
|----------|----------|--------------|
| URL query params | ✅ | ❌ |
| Checkbox selection | ✅ | ❌ |
| Delete operations | ✅ | ❌ |
| Export filtering | ✅ | ❌ |
| Display to user | ❌ | ✅ |
| Search/filter | ❌ | ✅ |

**Key files affected by this pattern:**
- `app/states/schema.py` - Add `id` field
- `app/states/deal_state.py` - Update `selected_deal_ids`, lookups, and URL redirects
- `app/pages/deals_page.py` - Update checkbox binding and click handlers
- `app/pages/review_page.py` - Update href links

### 8.3 Resetting Forms with `default_value` Inputs in Reflex
**Problem**: Form inputs using `default_value` only set their value on initial render. When navigating within an SPA (e.g., from `/add?mode=edit&id=...` to `/add`), React doesn't remount the component, so `on_mount` doesn't fire and `default_value` attrs retain stale data even after state is cleared.

**Solution**: Use a `form_key` counter in state that increments on reset, and wrap the form in a keyed container to force React remount:

```python
# In state
class DealFormState(rx.State):
    form_key: int = 0
    form_values: dict = {}
    
    @rx.event
    def reset_form(self):
        self.form_values = {}
        self.form_key += 1  # Force form remount

# In component - wrap form in keyed div
def deal_form_component() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            # ... form contents with default_value inputs ...
            on_submit=DealState.submit_deal,
        ),
        key=DealFormState.form_key,  # Key on OUTER container
    )
```

**For navbar links that should reset forms**: Use button + event sequence instead of anchor tags:
```python
rx.el.button(
    "Add New Deals",
    on_click=[DealFormState.reset_form, rx.redirect("/add")],
)
```

**Key insight**: The `key` prop must be on a container that wraps ALL the inputs you want to reset. When `form_key` changes, React treats it as a new component and remounts everything inside, causing `default_value` to re-initialize.
