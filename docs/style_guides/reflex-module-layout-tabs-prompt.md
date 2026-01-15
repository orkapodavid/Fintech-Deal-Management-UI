# Task: Group Module Pages into a Tabbed Module Layout

## Reference Documentation
- Read and follow your project's Reflex architecture guide, especially the sections on:
  - **Multi-region layout** (navigation, header, main content, sidebar)
  - **Shared layout components** under `app/components/shared/`
- If you do not have a guide yet, model your layout on a standard 4-region dashboard:
  - Region 1: Top navigation (fixed)
  - Region 2: Header / metrics strip (optional)
  - Region 3: Main content area (flex, scrollable)
  - Region 4: Sidebar / notifications (optional)

## Goal

Refactor the application so that **multiple pages within the same functional module** (e.g., Positions, PnL, Risk, Portfolio Tools) are **grouped into a single route** and displayed as **tabs** inside a shared `module_layout` component.

The `module_layout` should:
- Render the shared **top navigation** (Region 1).
- Render a shared **performance/header strip** (Region 2) if your app uses one.
- Render a **tab bar** for subpages within a module and an optional **controls row** (Region 3, top subregion).
- Render the **active subpage content** below the tab bar (Region 3, main subregion).
- Render a **notifications/sidebar panel** if applicable (Region 4).

## Target Layout Component

Create a shared layout component with the following signature (file location is a recommendation; adapt to your project structure):

```python
# app/components/shared/module_layout.py

import reflex as rx

from app.components.shared.top_navigation import top_navigation
from app.components.shared.performance_header import performance_header
from app.components.shared.notification_sidebar import notification_sidebar
from app.constants import FINANCIAL_GREY, DEFAULT_FONT


def sub_tab_link(name: str, base_url: str, current_subtab: str) -> rx.Component:
    """Render a single subtab as a link/button in the tab bar."""
    slug = (
        name.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace("(", "")
        .replace(")", "")
    )

    url = f"/{base_url}/{slug}"
    is_active = current_subtab == name

    return rx.link(
        rx.el.button(
            name,
            class_name=rx.cond(
                is_active,
                "px-3 h-full text-[9px] font-black text-blue-600 border-b-2 border-blue-600 uppercase tracking-tighter whitespace-nowrap",
                "px-3 h-full text-[9px] font-bold text-gray-400 border-b-2 border-transparent hover:text-gray-600 uppercase tracking-tighter whitespace-nowrap",
            ),
        ),
        href=url,
        class_name="h-full flex items-center",
    )


def module_layout(
    content: rx.Component,
    module_name: str,
    subtab_name: str,
    subtabs: list[str],
) -> rx.Component:
    """Shared layout wrapper for all module pages using a tab bar for subpages."""
    module_slug = module_name.lower().replace(" ", "-")

    return rx.el.div(
        # Region 1: Top navigation
        top_navigation(),
        # Region 2: Header / metrics strip (optional)
        performance_header(),
        # Regions 3 & 4: Main content with optional notifications/sidebar
        rx.el.div(
            # Region 3: Contextual workspace (tabs, controls, content)
            rx.el.div(
                # Subtab bar
                rx.el.div(
                    rx.foreach(
                        subtabs,
                        lambda name: sub_tab_link(name, module_slug, subtab_name),
                    ),
                    class_name=(
                        "flex flex-row items-center bg-white border-b border-gray-200 "
                        "px-2 pt-0.5 overflow-hidden shrink-0 h-[28px] w-full max-w-full flex-nowrap"
                    ),
                ),
                # Optional controls / breadcrumb strip
                rx.el.div(
                    rx.text(
                        f"{module_name} > {subtab_name}",
                        class_name="text-[10px] font-bold text-gray-400",
                    ),
                    class_name=(
                        "flex items-center justify-between px-3 py-1.5 bg-[#F9F9F9] "
                        "border-b border-gray-200 shrink-0 h-[40px]"
                    ),
                ),
                # Main tab content region
                rx.el.div(
                    content,
                    class_name="flex-1 flex flex-col min-h-0 overflow-hidden bg-white",
                ),
                class_name="flex flex-col flex-1 min-h-0 h-full border-r border-gray-200",
            ),
            # Region 4: Notification/sidebar area (optional)
            notification_sidebar(),
            class_name=(
                f"flex flex-1 overflow-hidden min-h-0 bg-[{FINANCIAL_GREY}] w-full"
            ),
        ),
        class_name=(
            f"flex flex-col h-screen w-screen bg-[{FINANCIAL_GREY}] "
            f"font-['{DEFAULT_FONT}'] antialiased overflow-hidden"
        ),
    )
```

> If your project uses different shared components (e.g., no `performance_header` or no `notification_sidebar`), adapt the imports and layout accordingly while preserving the **overall pattern** (navigation + header + tab bar + content + optional sidebar).

## Implementation Steps

1. **Identify Modules and Subpages**
   - List the major functional modules in your app (e.g., Positions, PnL, Risk, Compliance, Portfolio Tools).
   - For each module, list the existing pages that should become **subtabs** (e.g., Positions → Stocks, Bonds, Warrants).

2. **Define Routes and URL Scheme**
   - Choose a clean URL structure where each module has a base route and each subtab is a child path:
     - `/{module_slug}` (optional index tab)
     - `/{module_slug}/{subtab_slug}` (one per subtab)
   - Ensure `sub_tab_link` builds URLs that match your routing scheme.

3. **Create or Update Page Components**
   - For each module, create a single "hub" page component that uses `module_layout` and switches the `content` based on the active subtab.
   - Example pattern (pseudo-code):

     ```python
     # app/pages/positions/positions_page.py
     import reflex as rx

     from app.components.shared.module_layout import module_layout
     from app.components.positions.positions_views import (
         stock_positions_view,
         bond_positions_view,
         warrant_positions_view,
     )


     def positions_page(subtab: str = "Stocks") -> rx.Component:
         subtabs = ["Stocks", "Bonds", "Warrants"]

         view_by_name = {
             "Stocks": stock_positions_view(),
             "Bonds": bond_positions_view(),
             "Warrants": warrant_positions_view(),
         }

         content = view_by_name.get(subtab, stock_positions_view())

         return module_layout(
             content=content,
             module_name="Positions",
             subtab_name=subtab,
             subtabs=subtabs,
         )
     ```

   - Wire this page to multiple routes (one per subtab) if your router supports path params, or create thin wrapper pages that call the same hub component with different `subtab` values.

4. **Integrate with Navigation and State**
   - Update the top navigation to link to the **module base route** or a default subtab.
   - If you have a global `UIState`, ensure it tracks the active module and optionally the active tab per module.
   - Keep **business logic and data loading** in state + services; `module_layout` should remain a **pure layout component**.

5. **Preserve or Redirect Legacy Routes (Optional)**
   - If you are consolidating existing routes (e.g., `/stocks`, `/bonds`) into a single module route with tabs, either:
     - Keep the old routes as thin wrappers that delegate to the new tabbed layout, or
     - Add redirects so users/bookmarks still resolve correctly.

## Constraints

- **Do not** move business logic (data fetching, transformations) into `module_layout`.
  - Layout components should only compose UI and call child views/states.
- Prefer **flat state structure**: each module keeps its own state class; cross-module access uses `get_state()` as needed.
- Use `class_name` with Tailwind-style utility classes for styling, and keep typography/spacing consistent with your design tokens.
- Keep the layout **responsive** (flex layout, min-h-0, overflow handling) so the tabbed workspace behaves well at different viewport sizes.

## Verification Checklist

- [ ] Each module has a single, shared layout route using `module_layout`.
- [ ] Subtabs render in a horizontal tab bar and clearly indicate the active tab.
- [ ] Switching tabs updates **only the main content area**, not the navigation/header.
- [ ] All previous module pages are still reachable (either via tabs or via redirects).
- [ ] Layout works correctly across common viewport sizes (desktop, tablet, mobile).
- [ ] State and service logic remain untouched or are only minimally adapted to the new tabbed structure.
