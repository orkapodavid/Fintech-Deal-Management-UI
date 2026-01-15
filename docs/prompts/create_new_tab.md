# Task: Create a New Tab for an Existing Module Page

## User Clarification Required

Before proceeding, please confirm or provide the following information:

1. **Parent Module**: Which existing module is this tab for? (e.g., "Deals", "Trades")
2. **Tab Name**: What should the tab be called? (e.g., "Analytics", "History", "Settings")
3. **Tab Purpose**: Brief description of what this tab does
4. **Route Slug**: What URL slug for this tab? (e.g., "analytics" → `/deals/analytics`)
5. **Data Requirements**: Does this tab need its own state/data? (Yes/No)
6. **Form Required**: Does this tab contain a form for data entry? (Yes/No)

---

## Reference Documentation
Read and follow: `docs/style_guides/reflex-architecture-guide.md`

## Overview

This prompt guides adding a new tab to an existing module, following the established patterns in this project (e.g., how `add_page.py` was added to the Deals module).

---

## Files to Create/Modify

### 1. Tab View Component
**File**: `app/pages/{module}/{tab_slug}_page.py`

Create the view function for the new tab content:

```python
import reflex as rx
from app.states.{module}.{module}_state import {Module}State


def {module}_{tab_slug}_view() -> rx.Component:
    """
    {Tab Name} view content for the {Module} module.
    This is rendered inside the module_layout wrapper.
    """
    return rx.el.div(
        # Main content wrapper
        rx.el.div(
            # Header section
            rx.el.div(
                rx.el.h1(
                    "{Tab Name}",
                    class_name="text-2xl font-bold text-gray-900",
                ),
                rx.el.p(
                    "Description of what this tab does.",
                    class_name="text-sm text-gray-500 mt-1",
                ),
                class_name="mb-6",
            ),
            # Main content area
            rx.el.div(
                # Add your tab-specific content here
                # Could be a table, form, cards, charts, etc.
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100",
            ),
            class_name="w-full px-4 py-6",
        ),
        class_name="min-h-screen bg-gray-50",
        # Optional: Add on_mount handler if data needs to load
        # on_mount={Module}State.load_{tab_slug}_data,
    )
```

---

### 2. State Mixin (if tab needs its own logic)
**File**: `app/states/{module}/mixins/{tab_slug}_mixin.py`

If this tab requires its own state management:

```python
import reflex as rx
from app.services.{module}_service import {Module}Service

{module}_service = {Module}Service()


class {Module}{TabName}Mixin(rx.State, mixin=True):
    """Mixin for {Tab Name} tab logic."""
    
    # Tab-specific state variables
    {tab_slug}_data: list[dict] = []
    is_loading: bool = False
    
    # Add tab-specific variables as needed
    # E.g., filters, selected items, form data
    
    @rx.event
    def load_{tab_slug}_data(self):
        """Load data for this tab."""
        self.is_loading = True
        # Load data from service
        self.is_loading = False
    
    # Add more event handlers as needed
```

---

### 3. Update Main Module State
**File**: `app/states/{module}/{module}_state.py`

Add the new mixin to the composed state:

```python
import reflex as rx
from app.states.{module}.mixins.list_mixin import {Module}ListMixin
from app.states.{module}.mixins.{tab_slug}_mixin import {Module}{TabName}Mixin  # NEW


class {Module}State(
    {Module}ListMixin,
    {Module}{TabName}Mixin,  # NEW
    rx.State,
):
    """Main state for {Module} section, composing all mixins."""
    pass
```

---

### 4. Update Hub Page Component
**File**: `app/pages/{module}/{module}_page.py`

Add the new tab to the tab definitions and create a page function:

```python
import reflex as rx
from app.components.shared.module_layout import module_layout
from app.pages.{module}.list_page import {module}_list_view
from app.pages.{module}.{tab_slug}_page import {module}_{tab_slug}_view  # NEW


# Tab definitions - ADD NEW TAB HERE
{MODULE}_TABS = [
    {"name": "List", "id": "list", "route": "/{module}/list"},
    {"name": "Add New", "id": "add", "route": "/{module}/add"},
    {"name": "{Tab Name}", "id": "{tab_slug}", "route": "/{module}/{tab_slug}"},  # NEW
]


# Existing page functions...


def {module}_{tab_slug}_page() -> rx.Component:  # NEW
    """{Tab Name} page with tabbed module layout."""
    return module_layout(
        content={module}_{tab_slug}_view(),
        module_name="{Module}",
        tabs={MODULE}_TABS,
    )
```

---

### 5. Register Route
**File**: `app/app.py`

Add the route for the new tab:

```python
from app.pages.{module}.{module}_page import (
    {module}_list_page,
    {module}_add_page,
    {module}_{tab_slug}_page,  # NEW
)
from app.states.{module}.{module}_state import {Module}State
from app.states.ui.ui_state import UIState

# Existing routes...

# NEW: Register {Tab Name} route
app.add_page(
    {module}_{tab_slug}_page,
    route="/{module}/{tab_slug}",
    title="{Module} - {Tab Name}",
    on_load=[
        UIState.set_module("{Module}"),
        UIState.set_tab("{tab_slug}"),
        # Add data loading if needed:
        # {Module}State.load_{tab_slug}_data,
    ],
)
```

---

### 6. Optional: Add Module-Specific Components
**File**: `app/components/{module}/{tab_slug}_components.py`

If the tab needs reusable components:

```python
import reflex as rx
from app.states.{module}.{module}_state import {Module}State


def {tab_slug}_card(data: dict) -> rx.Component:
    """Reusable card component for {Tab Name} tab."""
    return rx.el.div(
        # Card content
        class_name="bg-white p-4 rounded-lg shadow-sm border border-gray-100",
    )


def {tab_slug}_table() -> rx.Component:
    """Table component for {Tab Name} tab."""
    return rx.el.table(
        # Table content
        class_name="min-w-full divide-y divide-gray-200",
    )
```

---

## Example: Adding an "Analytics" Tab to Deals Module

**Summary of files to create/modify:**

```
app/
├── states/deals/
│   ├── {module}_state.py          # MODIFY: Add mixin import
│   └── mixins/
│       └── analytics_mixin.py     # CREATE: Tab-specific state
│
├── pages/deals/
│   ├── deals_page.py              # MODIFY: Add tab definition + page function
│   └── analytics_page.py          # CREATE: Tab view component
│
└── app.py                         # MODIFY: Add route registration
```

---

## Patterns to Follow

### 1. Tab View Structure
Follow the pattern in `app/pages/deals/add_page.py`:
- Main container `rx.el.div` with `min-h-screen bg-gray-50`
- Inner container with `w-full px-4 py-6`
- Header with title and description
- Content sections with `bg-white p-6 rounded-xl shadow-sm border border-gray-100`

### 2. State Integration
Follow the pattern in `app/states/deals/mixins/add_mixin.py`:
- Use `rx.State, mixin=True` for mixin classes
- Use `@rx.event` decorator for event handlers
- Use `@rx.var(cache=True)` for computed properties
- Access service layer for data operations

### 3. Route Registration
Follow the pattern in `app/app.py`:
- Use `on_load` list for initializing tab state
- Always set `UIState.set_module()` and `UIState.set_tab()`
- Add data loading events if the tab needs data on mount

---

## Verification Checklist

- [ ] Tab view component created in `app/pages/{module}/{tab_slug}_page.py`
- [ ] State mixin created (if needed) in `app/states/{module}/mixins/{tab_slug}_mixin.py`
- [ ] Main state updated to include new mixin
- [ ] Tab added to `{MODULE}_TABS` in hub page
- [ ] Page function added to hub page
- [ ] Route registered in `app/app.py`
- [ ] Application compiles without errors
- [ ] Tab appears in navigation
- [ ] Tab content renders correctly
- [ ] Navigation between tabs works
