# Reflex Style Migration Prompts

Prompt templates for LLM agents to apply structured architecture patterns to existing or new Reflex applications. Use these prompts in conjunction with `docs/style_guides/reflex-architecture-guide.md`.

**Purpose**: These prompts help ensure consistent application of architectural patterns across different Reflex projects, regardless of domain (e-commerce, dashboards, CRM, analytics, etc.).

---

## Table of Contents

1. [Comprehensive Refactoring Prompt](#1-comprehensive-refactoring-prompt)
2. [Phase-Based Prompts](#2-phase-based-prompts)
3. [Quick Single-Shot Prompt](#3-quick-single-shot-prompt)
4. [Module-Specific Prompts](#4-module-specific-prompts)
5. [New Project Setup Prompt](#5-new-project-setup-prompt)
6. [Domain-Specific Adaptations](#6-domain-specific-adaptations)

---

## 1. Comprehensive Refactoring Prompt

Use this template for a complete refactoring of an existing Reflex application:

```markdown
# Task: Refactor Reflex Application to Structured Architecture

## Reference Documentation
Read and follow: `docs/style_guides/reflex-architecture-guide.md`

## Current Application Context
- **Application Name**: [Your App Name]
- **Domain**: [e.g., E-commerce, Dashboard, CRM, Analytics, Content Management]
- **Current Structure**: [Brief description of existing layout and organization]
- **Primary Features/Modules**: [List main features]
- **Pain Points**: [What problems are we solving with this refactor?]

## Refactoring Goals

### 1. Project Structure
Reorganize files following the recommended structure:
```
app/
├── app.py                  # Main entry, routes
├── constants.py            # Design tokens
├── components/
│   ├── shared/             # Layout components
│   └── {module}/           # Module components
├── states/
│   ├── ui/                 # Global UI state
│   └── {module}/           # Module states with mixins
├── services/
│   └── {module}/           # Business logic
└── pages/
    └── {module}/           # Page components
```

### 2. Layout Implementation
Apply multi-region layout pattern:
- Region 1: Navigation (fixed top, 40-60px)
- Region 2: Header/Metrics (optional, collapsible)
- Region 3: Main Content Area (flex, scrollable)
- Region 4: Sidebar (optional, collapsible)

### 3. State Management
Refactor states following these patterns:
- Create `UIState` for global UI concerns (navigation, sidebar, theme)
- Create module-specific states inheriting from `rx.State`
- Use mixins for feature-specific logic (`mixin=True`)
- Define `TypedDict` types for all data structures
- Use `@rx.var(cache=True)` for computed properties

### 4. Service Layer
Implement service layer:
- Move all business logic from states to services
- States only call services for data operations
- Services handle: API calls, database queries, data processing
- Add proper error handling and logging

### 5. Component Organization
Reorganize components:
- Create `{module}_views.py` for each module
- Use reusable patterns: `header_cell()`, `data_cell()`, `status_badge()`
- Export public components via `__init__.py`
- Implement loading, empty, and error states

### 6. Styling Standardization
Apply consistent styling:
- Use `class_name` with Tailwind CSS (not `style={}`)
- Define design tokens in `constants.py`
- Use consistent spacing, typography, and colors
- Add hover/focus states for interactivity

## Modules to Refactor
1. **[Module 1]**: [Current location] → [Target structure]
2. **[Module 2]**: [Current location] → [Target structure]
3. **[Module 3]**: [Current location] → [Target structure]

## Constraints
- Preserve all existing functionality
- Maintain backward-compatible route URLs (or document changes)
- Keep data integrity during migration
- Ensure no regressions in user experience

## Deliverables Checklist
- [ ] Project structure reorganized
- [ ] Multi-region layout implemented
- [ ] States refactored with mixins
- [ ] Service layer created
- [ ] Components reorganized with exports
- [ ] Tailwind styling applied consistently
- [ ] All routes registered and working
- [ ] Application tested and functional
```

---

## 2. Phase-Based Prompts

For large applications, break refactoring into manageable phases:

### Phase 1: Project Structure & Layout

```markdown
# Task: Implement Project Structure and Multi-Region Layout

## Reference
Read `docs/style_guides/reflex-architecture-guide.md` Sections 2-3

## Objectives

### 1. Create Directory Structure
```
app/
├── components/
│   └── shared/
│       ├── __init__.py
│       ├── navigation.py
│       ├── header.py
│       ├── sidebar.py
│       └── layout.py
├── states/
│   └── ui/
│       └── ui_state.py
└── constants.py
```

### 2. Create Design Tokens (`constants.py`)
Define colors, dimensions, typography:
- Primary/secondary/semantic colors
- Navigation, header, sidebar dimensions
- Font families and common sizes
- Border radius and shadow values

### 3. Implement UIState (`states/ui/ui_state.py`)
Create global UI state with:
- `active_module`, `active_tab` tracking
- `is_sidebar_open`, `is_mobile_menu_open` toggles
- `MODULE_TABS` configuration dictionary
- Computed vars: `current_tabs`, `active_tab`
- Event handlers: `set_module()`, `set_tab()`, `toggle_sidebar()`

### 4. Create Layout Components
Implement the 4-region layout:
- `navigation.py`: Top nav with module switching
- `header.py`: Metrics/KPI display (optional)
- `sidebar.py`: Collapsible right sidebar (optional)
- `layout.py`: Page wrapper with tab bar and toolbar

### 5. Update Main App
Modify `app.py` to use the new layout structure

## Constraints
- Existing functionality should continue working
- Place existing content in Region 3 (main content area)
- Do not modify business logic yet

## Verification
- [ ] App loads with new layout
- [ ] Navigation switches between modules
- [ ] Sidebar toggles open/closed
- [ ] Responsive on mobile viewports
```

### Phase 2: State Management Refactoring

```markdown
# Task: Refactor State Management

## Reference
Read `docs/style_guides/reflex-architecture-guide.md` Section 4

## Objectives

### 1. Create Type Definitions
For each module, create `states/{module}/types.py`:
- Define `TypedDict` for each data structure
- Use proper type hints (str, int, bool, list, Optional)

### 2. Create State Mixins
For each feature within a module:
- Create `states/{module}/mixins/{feature}_mixin.py`
- Use `rx.State, mixin=True`
- Include: data list, loading state, error state, search/filters
- Implement `load_data()` async method
- Add `@rx.var(cache=True)` for filtered data

### 3. Create Module States
For each module:
- Create `states/{module}/{module}_state.py`
- Inherit from all feature mixins
- Add shared state: `sort_column`, `sort_direction`, `selected_id`
- Implement `toggle_sort()`, `select_item()` handlers

### 4. Update UIState
- Add `MODULE_TABS` configuration for all modules
- Ensure `set_module()` initializes default tab

### 5. Update Components
- Import state from new locations
- Update state variable references
- Verify computed vars work correctly

## Constraints
- States should NOT contain business logic
- Use `@rx.event` for all handlers
- Use `@rx.var(cache=True)` for expensive computed vars
- Log errors with `logging.exception()`

## Verification
- [ ] All states load without errors
- [ ] Data loads correctly on page navigation
- [ ] Filters and sorting work
- [ ] Selection state updates properly
```

### Phase 3: Service Layer Implementation

```markdown
# Task: Implement Service Layer

## Reference
Read `docs/style_guides/reflex-architecture-guide.md` Section 5

## Objectives

### 1. Create Service Structure
```
app/services/
├── __init__.py           # Export all services
├── shared/
│   ├── __init__.py
│   └── database_service.py
└── {module}/
    ├── __init__.py
    └── {module}_service.py
```

### 2. Implement Base Database Service (if needed)
Create `shared/database_service.py`:
- Connection management
- Query execution methods
- Transaction handling

### 3. Create Module Services
For each module, create `{module}_service.py`:
- CRUD operations: `get_items()`, `get_by_id()`, `create()`, `update()`, `delete()`
- Business logic methods
- Proper error handling with logging
- Type hints for parameters and returns

### 4. Update Service Exports
In `services/__init__.py`:
- Import all services
- Define `__all__` list

### 5. Migrate Logic from States
- Move data fetching from states to services
- Move business logic to services
- States only call service methods

### 6. Update State Mixins
Modify state methods to use services:
```python
async def load_data(self):
    self.is_loading = True
    try:
        service = ModuleService()
        self.data = await service.get_items()
    except Exception as e:
        self.error = str(e)
        logging.exception(f"Error: {e}")
    finally:
        self.is_loading = False
```

## Constraints
- Services should be stateless
- Services should not import Reflex
- All external calls (DB, API) go through services
- Use async/await for I/O operations

## Verification
- [ ] Services can be instantiated independently
- [ ] Data loads correctly via services
- [ ] Error handling works properly
- [ ] Logging captures errors
```

### Phase 4: Component Organization & Styling

```markdown
# Task: Organize Components and Apply Styling

## Reference
Read `docs/style_guides/reflex-architecture-guide.md` Sections 6-7

## Objectives

### 1. Create Component Structure
```
app/components/{module}/
├── __init__.py           # Exports
└── {module}_views.py     # All views
```

### 2. Implement Reusable Components
Create shared component patterns:
- `header_cell(text, column_key, align, sortable)`
- `data_cell(value, align, mono)`
- `status_badge(status)`
- `loading_state()`
- `empty_state(message)`
- `error_state(message)`

### 3. Create Module Views
For each module:
- Table view with sorting and selection
- Card/grid view (if applicable)
- Detail view
- Form view (create/edit)

### 4. Export Components
Update `__init__.py` with:
- Named imports from views
- `__all__` list

### 5. Apply Consistent Styling
Using Tailwind via `class_name`:
- Consistent spacing (p-4, gap-4, etc.)
- Typography scale (text-sm, text-xs, font-medium)
- Color usage from constants
- Hover/focus states
- Loading animations

### 6. Implement Responsive Design
- Mobile-first approach
- Breakpoint handling (md:, lg:)
- Collapsible sidebar on mobile
- Responsive grid layouts

## Constraints
- Use `rx.el.*` for HTML elements
- Use `rx.*` for Radix components
- Use `class_name`, not `style={}`
- Radix sizes are '1'-'9', not 'sm'/'lg'

## Verification
- [ ] Components render correctly
- [ ] Styling is consistent across app
- [ ] Responsive on all viewports
- [ ] Interactive states work (hover, focus)
```

---

## 3. Quick Single-Shot Prompt

For smaller applications or rapid alignment:

```markdown
# Task: Apply Structured Architecture to Reflex App

Refactor this Reflex application following `docs/style_guides/reflex-architecture-guide.md`.

## Key Changes

1. **Project Structure**
   - Organize: `components/`, `states/`, `services/`, `pages/`
   - Create `constants.py` for design tokens

2. **Multi-Region Layout**
   - Region 1: Navigation (top, fixed)
   - Region 2: Header (optional, metrics)
   - Region 3: Main content (flex, scrollable)
   - Region 4: Sidebar (optional, collapsible)

3. **State Management**
   - Global `UIState` for navigation/sidebar
   - Module states with mixins for features
   - `TypedDict` definitions for data
   - `@rx.var(cache=True)` for filtered data

4. **Service Layer**
   - Move business logic to services
   - States call services for data
   - Pattern: State → Service → Data Source

5. **Styling**
   - Tailwind via `class_name`
   - Design tokens in `constants.py`
   - Consistent typography and spacing
   - Loading/empty/error states

## Approach
1. Set up project structure
2. Create layout components
3. Refactor states with mixins
4. Add service layer
5. Apply consistent styling

## Domain: [Specify your domain: e-commerce, dashboard, CRM, etc.]
```

---

## 4. Module-Specific Prompts

### Adding a New Module

```markdown
# Task: Add New Module Following Architecture Guide

## Reference
Read `docs/style_guides/reflex-architecture-guide.md` Section 9

## New Module Details
- **Module Name**: [ModuleName]
- **Purpose**: [What this module does]
- **Features/Tabs**: [List of features or tabs]
- **Data Types**: [Key data structures]

## Files to Create

### 1. Types (`app/states/{module}/types.py`)
```python
from typing import TypedDict

class {Item}Type(TypedDict):
    id: int
    name: str
    # ... other fields
```

### 2. Mixins (`app/states/{module}/mixins/{feature}_mixin.py`)
- Data state, loading, error, filters
- `load_data()` method
- `filtered_data` computed var

### 3. State (`app/states/{module}/{module}_state.py`)
- Inherit from mixins
- Sorting, selection state
- Event handlers

### 4. Service (`app/services/{module}/{module}_service.py`)
- CRUD operations
- Business logic
- Error handling

### 5. Components (`app/components/{module}/{module}_views.py`)
- Table/list view
- Card view (if needed)
- Detail view
- Form view

### 6. Pages (`app/pages/{module}/{page}_page.py`)
- Use layout wrapper
- Import module components

### 7. Integration
- Register routes in `app.py`
- Add to `UIState.MODULE_TABS`
- Add to navigation component

## Verification
- [ ] Module accessible via navigation
- [ ] Data loads correctly
- [ ] All views render properly
- [ ] CRUD operations work
```

### Refactoring a Single Module

```markdown
# Task: Refactor [ModuleName] Module

## Current State
- **Location**: [Current file paths]
- **Issues**: [Problems to solve]

## Target Structure
Following `docs/style_guides/reflex-architecture-guide.md`:

### 1. State Refactoring
- Split into: `{module}_state.py` + mixins
- Move business logic to service
- Add TypedDict types
- Use cached computed vars

### 2. Service Creation
- Create `{module}_service.py`
- Implement data operations
- Add error handling

### 3. Component Organization
- Create `{module}_views.py`
- Implement reusable patterns
- Add loading/empty/error states

### 4. Styling Alignment
- Apply Tailwind classes
- Use design tokens
- Ensure consistency

## Constraints
- Preserve existing functionality
- Maintain data structures
- Keep route URLs

## Deliverables
- [ ] State refactored
- [ ] Service created
- [ ] Components organized
- [ ] Styling applied
```

---

## 5. New Project Setup Prompt

For starting a new Reflex project with this architecture:

```markdown
# Task: Set Up New Reflex Project with Structured Architecture

## Project Details
- **Name**: [Project Name]
- **Domain**: [e.g., E-commerce, Dashboard, SaaS]
- **Description**: [Brief description]
- **Main Modules**: [List of 3-5 main modules]

## Reference
Follow `docs/style_guides/reflex-architecture-guide.md`

## Setup Steps

### 1. Initialize Project
```bash
mkdir {project-name}
cd {project-name}
reflex init
```

### 2. Create Directory Structure
```
app/
├── app.py
├── constants.py
├── components/
│   ├── __init__.py
│   └── shared/
│       ├── __init__.py
│       ├── navigation.py
│       ├── header.py
│       ├── sidebar.py
│       └── layout.py
├── states/
│   ├── __init__.py
│   ├── types.py
│   └── ui/
│       └── ui_state.py
├── services/
│   ├── __init__.py
│   └── shared/
│       └── database_service.py
└── pages/
    └── __init__.py
```

### 3. Configure App (`rxconfig.py`)
- Enable Tailwind plugin
- Set ports

### 4. Create Foundation
- `constants.py`: Design tokens
- `ui_state.py`: Global UI state
- Layout components
- Main `app.py` with layout

### 5. Create First Module
Use module templates from Section 9 of architecture guide

## Deliverables
- [ ] Project initialized
- [ ] Directory structure created
- [ ] Design tokens defined
- [ ] Layout components working
- [ ] First module implemented
- [ ] Routes registered
```

---

## 6. Domain-Specific Adaptations

Guidance for adapting the architecture to different domains:

### E-Commerce Application
```markdown
## Domain Considerations
- **Modules**: Products, Cart, Orders, Customers, Inventory
- **Layout**: Consider persistent cart sidebar
- **State**: Cart state needs cross-page persistence
- **Services**: Payment gateway integration, inventory checks

## Specific Patterns
- Product listing with filters (price, category, availability)
- Cart management with quantity updates
- Checkout flow with form validation
- Order status tracking
```

### Analytics Dashboard
```markdown
## Domain Considerations
- **Modules**: Overview, Reports, Data Sources, Settings
- **Layout**: Emphasize Region 2 for KPI metrics
- **State**: Date range filters across all views
- **Services**: Data aggregation, chart data preparation

## Specific Patterns
- KPI cards with trend indicators
- Chart components (consider recharts/ag-charts)
- Date range picker persistence
- Export functionality (CSV, PDF)
```

### CRM Application
```markdown
## Domain Considerations
- **Modules**: Contacts, Companies, Deals, Tasks, Reports
- **Layout**: Activity timeline in sidebar
- **State**: Selected entity context across views
- **Services**: Contact enrichment, email integration

## Specific Patterns
- Contact/company detail views
- Deal pipeline with drag-drop stages
- Activity logging and timeline
- Search across all entities
```

### Content Management
```markdown
## Domain Considerations
- **Modules**: Content, Media, Categories, Users, Settings
- **Layout**: Preview panel in sidebar
- **State**: Draft/publish status management
- **Services**: Media upload, content versioning

## Specific Patterns
- Rich text editor integration
- Media library with upload
- Content scheduling
- Version history
```

---

## Usage Tips

1. **Start with the Reference**: Always point to `docs/style_guides/reflex-architecture-guide.md`

2. **Fill Placeholders**: Replace all `[bracketed]` items with your specifics

3. **Choose Appropriate Prompt**: 
   - New project → Use Setup Prompt
   - Full refactor → Use Comprehensive Prompt
   - Large app → Use Phase-Based Prompts
   - Single module → Use Module-Specific Prompts

4. **Verify Each Phase**: Test the app after each phase before proceeding

5. **Preserve Functionality**: Emphasize that existing features must continue working

6. **Domain Adaptation**: Review domain-specific guidance for relevant patterns

---

## Related Documentation

- `docs/style_guides/reflex-architecture-guide.md` - Complete architecture reference
- `.agents/skills/reflex-dev/references/` - Reflex framework documentation
- `AGENTS.md` - Project-specific instructions
