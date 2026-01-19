# Task: Create a New Module Page

## User Clarification Required

Before proceeding, please confirm or provide the following information:

1. **Module Name**: What is the name of the module? (e.g., "Trades", "Reports", "Settings")
2. **Module Purpose**: Brief description of what this module does
3. **Tab Structure**: What tabs/sub-pages should this module have? (e.g., ["List", "Add New", "Details"])
4. **Data Entity**: What is the primary data entity? (e.g., "Trade", "Report")
5. **Key Fields**: List the main fields for the data entity (e.g., id, name, status, created_at)
6. **Route Base**: What should be the base URL route? (e.g., `/trades`, `/reports`)

---

## Overview

This prompt guides the creation of a complete module page following established Reflex patterns:
- Multi-region layout with navigation, tabs, content, and sidebar
- State management with mixins
- Service layer for business logic
- Component organization

## Files to Create

### 1. Types Definition
**File**: `app/states/{module}/types.py`

```python
from typing import TypedDict, Optional

class {Entity}Type(TypedDict):
    id: str
    # Add fields based on user requirements
    name: str
    status: str
    created_at: str
    updated_at: str
```

---

### 2. State Mixins (one per tab/feature)
**Directory**: `app/states/{module}/mixins/`

For each tab, create a mixin following this pattern:

**File**: `app/states/{module}/mixins/list_mixin.py`
```python
import reflex as rx
from app.services.{module}_service import {Module}Service

{module}_service = {Module}Service()

class {Module}ListMixin(rx.State, mixin=True):
    """Mixin for {Module} list view logic."""
    
    # Data state
    items: list[dict] = []
    is_loading: bool = False
    
    # Filter/search state
    search_query: str = ""
    filter_status: str = "all"
    
    # Pagination
    current_page: int = 1
    items_per_page: int = 25
    
    # Sorting
    sort_column: str = ""
    sort_direction: str = "asc"
    
    # Selection
    selected_ids: list[str] = []
    
    @rx.event
    def load_data(self):
        """Load data from service."""
        self.items = {module}_service.get_items()
    
    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.current_page = 1
    
    @rx.event
    def sort_by_column(self, column: str):
        if self.sort_column == column:
            self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"
        else:
            self.sort_column = column
            self.sort_direction = "asc"
    
    @rx.var(cache=True)
    def filtered_items(self) -> list[dict]:
        """Filter items based on search and filters."""
        data = self.items
        if self.search_query:
            query = self.search_query.lower()
            data = [item for item in data if query in item.get("name", "").lower()]
        return data
```

---

### 3. Main Module State
**File**: `app/states/{module}/{module}_state.py`

```python
import reflex as rx
from app.states.{module}.mixins.list_mixin import {Module}ListMixin
# Import other mixins as needed

class {Module}State(
    {Module}ListMixin,
    # Add other mixins
    rx.State,
):
    """Main state for {Module} section, composing all mixins."""
    pass
```

**File**: `app/states/{module}/__init__.py`
```python
from .{module}_state import {Module}State
```

---

### 4. Service Layer
**File**: `app/services/{module}_service.py`

```python
from typing import List, Optional

class {Module}Service:
    def __init__(self):
        self._items: List[dict] = []
        self._initialized = False

    def get_items(self) -> List[dict]:
        if not self._initialized:
            self._generate_mock_data()
            self._initialized = True
        return self._items

    def get_by_id(self, item_id: str) -> Optional[dict]:
        return next((item for item in self._items if item["id"] == item_id), None)

    def save(self, item: dict) -> dict:
        existing_index = next(
            (i for i, d in enumerate(self._items) if d["id"] == item["id"]), 
            None
        )
        if existing_index is not None:
            self._items[existing_index] = item
        else:
            self._items.append(item)
        return item

    def delete(self, item_id: str) -> bool:
        initial_len = len(self._items)
        self._items = [item for item in self._items if item["id"] != item_id]
        return len(self._items) < initial_len

    def _generate_mock_data(self):
        """Generate mock data for development."""
        import uuid
        from datetime import datetime
        
        for i in range(25):
            self._items.append({
                "id": str(uuid.uuid4()),
                "name": f"Item {i + 1}",
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            })
```

Update `app/services/__init__.py` to export the new service.

---

### 5. Hub Page Component (Route Handler)
**File**: `app/pages/{module}/{module}_page.py`

```python
"""
{Module} module page with tabbed layout.

This is the hub component that renders the module with tab navigation.
Each tab displays a different view within the shared module layout.
"""

import reflex as rx
from app.components.shared.module_layout import module_layout
from app.pages.{module}.list_page import {module}_list_view
# Import other tab views

# Tab definitions for the module
{MODULE}_TABS = [
    {"name": "List", "id": "list", "route": "/{module}/list"},
    {"name": "Add New", "id": "add", "route": "/{module}/add"},
    # Add more tabs as needed
]


def {module}_list_page() -> rx.Component:
    """List page with tabbed module layout."""
    return module_layout(
        content={module}_list_view(),
        module_name="{Module}",
        tabs={MODULE}_TABS,
    )


def {module}_add_page() -> rx.Component:
    """Add page with tabbed module layout."""
    return module_layout(
        content={module}_add_view(),
        module_name="{Module}",
        tabs={MODULE}_TABS,
    )
```

---

### 6. Tab View Components
**File**: `app/pages/{module}/list_page.py`

Each tab gets its own view file with the actual content:

```python
import reflex as rx
from app.states.{module}.{module}_state import {Module}State


def {module}_list_view() -> rx.Component:
    """List view content (used inside module layout)."""
    return rx.el.div(
        # Toolbar
        rx.el.div(
            # Search, filters, actions
            class_name="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between",
        ),
        # Table
        rx.el.div(
            rx.el.table(
                # Table content
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="overflow-auto flex-1",
        ),
        # Pagination
        rx.el.div(
            # Pagination controls
            class_name="bg-white px-6 py-4 border-t border-gray-200",
        ),
        class_name="flex-1 flex flex-col min-w-0 bg-white h-full",
    )
```

---

### 7. Route Registration
**File**: Update `app/app.py`

```python
from app.pages.{module}.{module}_page import (
    {module}_list_page,
    {module}_add_page,
)
from app.states.{module}.{module}_state import {Module}State
from app.states.ui.ui_state import UIState

# Register routes
app.add_page(
    {module}_list_page,
    route="/{module}/list",
    title="{Module} - List",
    on_load=[UIState.set_module("{Module}"), UIState.set_tab("list"), {Module}State.load_data],
)

app.add_page(
    {module}_add_page,
    route="/{module}/add", 
    title="{Module} - Add",
    on_load=[UIState.set_module("{Module}"), UIState.set_tab("add")],
)
```

---

### 8. Navigation Integration
Update `app/components/shared/navigation.py` to include the new module in the navigation bar.

---

## Directory Structure Summary

```
app/
├── states/{module}/
│   ├── __init__.py
│   ├── types.py
│   ├── {module}_state.py
│   └── mixins/
│       ├── __init__.py
│       └── list_mixin.py
│
├── services/
│   └── {module}_service.py
│
├── pages/{module}/
│   ├── __init__.py
│   ├── {module}_page.py      # Hub with all page functions
│   └── list_page.py          # Tab view implementation
│
└── components/{module}/       # Optional: module-specific components
    ├── __init__.py
    └── {module}_views.py
```

---

## Verification Checklist

- [ ] Types defined in `app/states/{module}/types.py`
- [ ] Mixins created in `app/states/{module}/mixins/`
- [ ] Main state created in `app/states/{module}/{module}_state.py`
- [ ] Service created in `app/services/{module}_service.py`
- [ ] Hub page created in `app/pages/{module}/{module}_page.py`
- [ ] Tab views created in `app/pages/{module}/`
- [ ] Routes registered in `app/app.py`
- [ ] Navigation updated in `app/components/shared/navigation.py`
- [ ] Application compiles without errors
- [ ] Navigation works between tabs
- [ ] Data loads correctly
