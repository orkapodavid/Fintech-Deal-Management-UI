# Generic Prompt: Migrate Fintech Deal Management SPA to Route-Based Architecture (Fintech Deals App)

## Context

I have a **Reflex fintech deal management application** that manages a full deal pipeline:

- A **deals list / pipeline view** with filtering, sorting, pagination, selection, export, and bulk actions
- An **add / edit deal flow** backed by a structured bento-style deal form and validation
- A **review flow** where AI-ingested deals are reviewed, approved, or rejected
- A global **alert sidebar** showing validation and system alerts

The codebase originally followed a **state-based Single Page Application (SPA)** pattern and has been migrated toward a **route-based architecture**, but I want a clear, end‑to‑end migration guide tailored to this project.

The target routes for this app are:

- `/` → redirects to `/deals`
- `/deals` → main **deal pipeline** view
- `/deals/add` → **add / edit deal** flow
- `/deals/review` → **review queue + active review workspace**

This prompt should use the actual modules in this repo: `DealState`, `DealFormState`, `AlertState`, `/deals` pages, `navbar.py`, `deal_form_component.py`, and `alert_sidebar.py`.

---

## Current Architecture (This Repo)

### Routing & Layout

- `app/app.py`
  - Defines `index()`, `deals_page_wrapper()`, `add_page_wrapper()`, `review_page_wrapper()`
  - Registers:
    - `/` → `index()` which redirects to `/deals`
    - `/deals` → `deals_page_wrapper()` with `DealState.load_data` and `AlertState.generate_alerts`
    - `/deals/add` → `add_page_wrapper()`
    - `/deals/review` → `review_page_wrapper()` with `DealState.load_data` and `DealState.on_review_page_load`
  - `layout(content)` wraps all pages with the shared `navbar()`

### Pages (Views)

- `app/pages/deals/list_page.py`
  - `deals_list_page()` renders the **deal pipeline table** with search, filters, bulk actions, and pagination
- `app/pages/deals/add_page.py`
  - `deals_add_page()` renders the **ingestion source** (Upload PDF / Paste Text) plus the **"New Deal Details"** form via `deal_form_component()`
  - Uses `on_mount=DealFormState.on_page_load` to interpret URL mode on `/deals/add`
- `app/pages/deals/review_page.py`
  - `deals_review_page()` renders the **review workspace** (document panel + deal form) and a **pending review queue**

### Components

- `app/components/navbar.py`
  - `navbar()` renders the global navigation bar and wires up:
    - `navbar_link("Deals", "/deals")`
    - `add_new_deals_link()` which calls `DealFormState.reset_form` and redirects to `/deals/add`
    - `navbar_link("Review AI Input", "/deals/review")`
    - Search input bound to `DealState.set_search_query`
    - Refresh, alerts, settings, and logout actions
- `app/components/deal_form_component.py`
  - `deal_form_component()` is the **shared deal form** used on **Add** and **Review** pages
  - Reads and writes `DealFormState` (`form_values`, `validation_results`, `form_mode`, `form_key`)
  - Calls into `DealState` for actions like `submit_new_deal`, `save_draft`, `approve_current_deal`, `reject_current_deal`
- `app/components/alert_sidebar.py`
  - `alert_sidebar()` renders the **alert sidebar** controlled by `AlertState` (`alerts`, `show_sidebar`)

### State (Split-State Pattern)

- `app/states/deals/deals_state.py`
  - `DealState` is the **main Deals module state** composed from:
    - `DealListMixin` (`app/states/deals/mixins/list_mixin.py`)
      - Pipeline list, filters, sorting, pagination, selection, export, refresh
    - `DealAddMixin` (`app/states/deals/mixins/add_mixin.py`)
      - Add / edit flow, draft saving, submission, redirect to `/deals/add` with `mode`/`id`
    - `DealReviewMixin` (`app/states/deals/mixins/review_mixin.py`)
      - Review queue, `pending_deals`, `active_review_deal`, approve/reject and `/deals/review?id=...` behavior
  - Also handles navbar-related actions (`show_settings`, `show_notifications`, `logout`)
- `app/states/deal_form_state.py`
  - `DealFormState` is a **transient form state** that manages:
    - `form_mode` (`FormMode.ADD`, `FormMode.EDIT`, `FormMode.REVIEW`)
    - `form_values`, `validation_results`, `touched_fields`, `is_dirty`, `is_submitting`
    - `form_key` used to force a React remount of the form when resetting
  - Implements `on_page_load()` to read `mode` from URL params on `/deals/add`
  - Implements `load_deal_for_edit()` to populate the form for edit or review
- `app/states/alerts/alert_state.py`
  - `AlertState` keeps `alerts` and `show_sidebar` and exposes `toggle_sidebar`, `dismiss_alert`, `generate_alerts`, and `unread_count`

### Remaining SPA-style Issues

- Historically, navigation was **state-driven** (e.g., setting active tabs/pages) on a single route
- Some interactions still mix **navigation logic with stateful events** instead of relying purely on routes + URL parameters
- Add vs edit vs review modes can be confusing if URL parameters and state are not perfectly aligned
- We want a **clear, URL-driven mental model**: the route + query params define the mode; state reacts to those.

---

## Desired Architecture (For This Fintech Deals App)

### Route Structure

- `/` → redirects to `/deals`
- `/deals` → **deal pipeline** (list, filters, export, selection)
- `/deals/add` → **add deal** (fresh form, ingestion section)
- `/deals/add?mode=edit&id={deal_id}` → **edit existing deal**
- `/deals/review` → **review dashboard** (no active deal selected yet)
- `/deals/review?id={deal_id}` → **active review** of specific deal

### State Organization

- **Global Deals State** (`DealState`)
  - Holds the master list `deals` and view logic for pipeline, add, and review
  - Delegates to mixins:
    - `DealListMixin` → filters, sort, pagination, export, selection
    - `DealAddMixin` → creating, editing, drafting, and submitting deals
    - `DealReviewMixin` → pending queue, active review, approval/rejection
- **Deal Form State** (`DealFormState`)
  - Dedicated to form concerns only:
    - Field values, validation, touched fields, submit state
    - `form_mode` (add/edit/review)
    - `form_key` for reset/remount
  - Reads route params in `on_page_load()` and is used by `deal_form_component()`
- **Alert State** (`AlertState`)
  - Independent module tracking alert data and sidebar visibility
  - Integrated into navbar and `alert_sidebar()`

**Rule**: Keep **form-level state** in `DealFormState`, and keep **pipeline/review logic and deal collections** in `DealState` + its mixins. Use `self.get_state(DealFormState)` in mixins where necessary.

### File Structure (This Project)

```bash
app/
├── app.py
├── components/
│   ├── navbar.py              # Top nav: Deals, Add New Deals, Review AI Input, alerts, settings
│   ├── alert_sidebar.py       # Alerts sidebar controlled by AlertState
│   ├── deal_form_component.py # Shared deal form for Add + Review
│   └── confirmation_dialog.py
├── pages/
│   └── deals/
│       ├── list_page.py       # /deals – pipeline view
│       ├── add_page.py        # /deals/add – ingestion + deal form
│       └── review_page.py     # /deals/review – review queue + workspace
├── states/
│   ├── alerts/
│   │   └── alert_state.py     # AlertState
│   ├── deals/
│   │   ├── deals_state.py     # DealState (composes list/add/review)
│   │   └── mixins/
│   │       ├── list_mixin.py  # DealListMixin
│   │       ├── add_mixin.py   # DealAddMixin
│   │       └── review_mixin.py# DealReviewMixin
│   ├── deal_form_state.py     # DealFormState
│   └── schema.py              # Deal, Alert and enums
└── services/
    ├── deal_service.py        # DealService
    └── alert_service.py       # AlertService
```

---

## Tasks

### Phase 1: Investigation & Planning (2–4 hours)

1. **Analyze Routes & On-Load Behavior**
   - Confirm routes and on-load handlers in `app/app.py` match the desired architecture.
   - Verify `/deals` loads deals and alerts, `/deals/review` loads deals and interprets `id` via `DealReviewMixin.on_review_page_load`, and `/deals/add` uses `DealFormState.on_page_load`.

2. **Map Which State Drives Which View**
   - `/deals` uses `DealState.deals`, `filtered_deals`, `paginated_deals`, and associated events.
   - `/deals/add` uses `DealFormState` for the form plus `DealAddMixin` for submission and drafts.
   - `/deals/review` uses `DealReviewMixin.pending_deals`, `DealReviewMixin.active_review_deal`, and `DealFormState` in review mode.

3. **Review Navigation Points**
   - Navbar links/buttons in `navbar.py` → ensure they align with `/deals`, `/deals/add`, `/deals/review`.
   - List row clicks and review queue links → ensure they navigate via URL (including `id`) rather than hidden state-only switches.

4. **Document Current vs Target Behavior**
   - For each navigation path (e.g., "Edit Selected", "Review" from list, "Review" from queue), document:
     - Current implementation (events, redirects, state changes)
     - Desired route (`/deals/add?mode=edit&id=...`, `/deals/review?id=...`)
     - Which state handler should run on page load.

### Phase 2: State Restructuring (4–8 hours)

1. **Ensure Clear Responsibilities in Mixins**
   - `DealListMixin` → list concerns only (filters, sorting, pagination, selection, export, delete).
   - `DealAddMixin` → creating/editing deals, interacting with `DealFormState`, and redirecting to `/deals/add`.
   - `DealReviewMixin` → review queue, `pending_deals`, `active_review_deal` and actions (`approve_current_deal`, `reject_current_deal`).

2. **Enforce URL-Driven Modes in DealFormState**
   - `DealFormState.on_page_load()` should:
     - Read `mode` from `self.router.page.params.get("mode", "add")`.
     - Call `reset_form()` when not in edit mode.
     - Allow `DealAddMixin.edit_selected_deal()` to pre-load values and redirect to `/deals/add?mode=edit&id=...`.

3. **Use Deal IDs Everywhere for Identity**
   - Confirm all of the following use `deal.id` (not `ticker`) as the identifier:
     - Selection (`selected_deal_ids` in `DealListMixin`).
     - URL params for edit and review (`/deals/add?mode=edit&id={deal_id}`, `/deals/review?id={deal_id}`).
     - Delete operations and export filters.

4. **Keep Form State Isolated**
   - Avoid adding list or queue state into `DealFormState`.
   - Use `DealFormState.form_key` to reset default values across route transitions or mode changes.

### Phase 3: Page Wiring & Component Usage (3–5 hours)

1. **Deals List (`list_page.py`)**
   - Use `DealState` exclusively for deals data and list actions.
   - Keep `deals_list_page()` declarative:
     - Bind filters/search to `DealState.set_search_query`, `set_filter_status`, etc.
     - Bind bulk actions to `DealState.export_deals`, `DealState.edit_selected_deal`, `DealState.request_delete`.
     - Use `DealState.paginated_deals` with `rx.foreach` for rows.

2. **Add Page (`add_page.py`)**
   - Use `DealState.upload_tab` to control ingestion UI.
   - Render `deal_form_component()` as the central place for all deal fields.
   - Ensure `on_mount=DealFormState.on_page_load` is present so URL `mode` is respected.

3. **Review Page (`review_page.py`)**
   - Use `DealState.active_review_deal` to toggle between idle and active review states.
   - Use `DealState.pending_deals` to drive the queue.
   - Ensure queue links and any "Review" actions navigate with `/deals/review?id={deal.id}`.

4. **Navbar & Alerts Integration**
   - Keep navbar using links and redirects:
     - `navbar_link("Deals", "/deals")`
     - `add_new_deals_link()` → `DealFormState.reset_form` + redirect to `/deals/add`.
     - `navbar_link("Review AI Input", "/deals/review")`.
   - Use `AlertState` for alert counts and `alert_sidebar()` for the sidebar.

### Phase 4: Route Registration (2–3 hours)

1. **Verify `app/app.py` Matches the Target**
   - Confirm:
     - `/` redirects to `/deals`.
     - `/deals` loads data and alerts.
     - `/deals/add` uses `DealFormState.on_page_load` (via `on_mount` in `deals_add_page`).
     - `/deals/review` loads deals and calls `DealState.on_review_page_load`.

2. **Keep Titles and Metadata Accurate**
   - Ensure page titles accurately reflect their purpose:
     - `"Deals | HDP"`, `"Add Deal | HDP"`, `"Review Deals | HDP"`.

### Phase 5: Navigation Updates (3–4 hours)

1. **Replace Any Leftover State-Only Navigation**
   - Remove or refactor any remnants of `set_active_page`, `set_active_tab`, or similar SPA patterns.
   - Prefer `rx.link`/`rx.el.a` with `href` for navigation, letting states react to routes.

2. **Make Row/Queue Navigation Purely URL-Based Where Possible**
   - For pipeline rows and review queue rows, prefer:

     ```python
     rx.el.a(
         deal.ticker,
         href=rx.Var.create(f"/deals/review?id={deal.id}"),
         class_name="font-semibold text-blue-600 hover:underline",
     )
     ```

   - Then rely on `DealReviewMixin.on_review_page_load` + `DealFormState.load_deal_for_edit` to set state.

### Phase 6: Cleanup (2–3 hours)

1. **Remove Obsolete State & Handlers**
   - Delete unused state variables and events leftover from the SPA era.
   - Remove duplication between mixins and pages; views should call into mixin methods.

2. **Run Linting & Format Fixes**
   - Use `ruff` to catch unused imports and dead code:

     ```bash
     uv run ruff check .
     uv run ruff check . --fix
     ```

3. **Update Documentation**
   - Update `docs/` to show the real routes (`/deals`, `/deals/add`, `/deals/review`) and the split-state pattern.

### Phase 7: Testing (3–4 hours)

1. **Manual Testing**
   - Test routes:
     - `/`, `/deals`, `/deals/add`, `/deals/review`.
     - `/deals/add?mode=edit&id={existing_deal_id}`.
     - `/deals/review?id={pending_deal_id}`.
   - Verify:
     - URL changes correctly on navbar navigation and row/queue clicks.
     - Browser back/forward works across Deals / Add / Review.
     - Direct URL entry works for edit and review.
     - Deals and alerts load without errors on each page.

2. **Run Application**

   ```bash
   reflex run
   # or
   uv run reflex run

   # Open http://localhost:3000 and exercise all routes
   ```

3. **Testing Checklist**

   - [ ] All routes accessible
   - [ ] URL updates when clicking navigation
   - [ ] Browser back/forward works
   - [ ] Direct URL entry works (including `id` params)
   - [ ] Data loads correctly for each page
   - [ ] Navigation highlights are correct
   - [ ] No console errors
   - [ ] State persists appropriately where expected

---

## Key Principles

1. **URL Structure**
   - Use `/deals`, `/deals/add`, `/deals/review` for the three core flows.
   - Use `id` query params for deal identity and `mode` for add vs edit.

2. **State Organization**
   - Keep `DealState` responsible for the pipeline, add, and review workflows.
   - Keep `DealFormState` responsible only for form values, validation, and modes.
   - Keep `AlertState` responsible only for alerts and sidebar visibility.

3. **Data Loading**
   - Load deals via `DealState.load_data()` on routes that need them (`/deals`, `/deals/review`).
   - Load alerts via `AlertState.generate_alerts()` on `/deals`.
   - Only load what is necessary for the current route.

4. **Navigation**
   - Use `href`-based navigation for route changes.
   - Use URL params plus on-load handlers (`DealFormState.on_page_load`, `DealReviewMixin.on_review_page_load`) to configure state.

---

## Expected Benefits

- ✅ Bookmarkable, shareable URLs for Deals, Add, and Review flows
- ✅ Clear separation between global pipeline/review logic and form-level concerns
- ✅ Predictable behavior on page refresh and direct URL entry
- ✅ Easier debugging by mapping behavior to specific routes and states
- ✅ A clean, composable state structure (`DealState` + `DealFormState` + `AlertState`)

## Estimated Timeline

- **Small extension to this app** (current Deals module only): ~20–30 hours
- **Medium** (adding more sections with similar patterns): ~40–60 hours
- **Large** (multiple additional modules beyond Deals): ~60–100 hours

## Common Pitfalls to Avoid

1. **Don’t** keep SPA-style state navigation (e.g., `set_active_page`) once routes are established.
2. **Don’t** mix global and form state—keep `DealFormState` focused on form concerns.
3. **Don’t** use `ticker` as a primary identifier in URLs; always use `Deal.id`.
4. **Don’t** load all data on every route—load just what each page needs.
5. **Do** test navigation, refresh, and deep linking thoroughly.
6. **Do** ensure `form_key` usage correctly resets default values when changing modes/routes.
7. **Do** keep documentation up to date with the real routes and state modules.
