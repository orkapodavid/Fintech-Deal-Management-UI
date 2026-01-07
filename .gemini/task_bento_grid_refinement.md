# Implementation Plan: Bento Box Grid Layout Refinement

## Objective
Refine the deal entry form to follow a precise **12-column grid system** with specific column allocations, mobile-first responsiveness, and maximum information density for power users on 1080p displays.

---

## Current State Analysis
The initial Bento Box implementation is functional but uses arbitrary column counts (2-col, 5-col grids). The user's specifications require:
- **Precise 12-column grid** system
- **Identity (7 cols)** + **Classification (5 cols)** in top row
- **Combined Financials + Structure** with 4 fields per row in middle section
- **Horizontal strip** for Regulatory & Risk
- **Reduced vertical padding** for density
- **Responsive stacking** on smaller screens

---

## Technical Specifications

### Grid System
Using Tailwind CSS grid utilities via Reflex:
- `grid-cols-12` for the main container
- `col-span-X` for individual section column widths
- Responsive breakpoints: `lg:` prefix for 1024px+ (desktop)

### Column Allocations

| Section | Desktop (lg:) | Mobile |
|---------|---------------|--------|
| Identity | `col-span-7` | `col-span-12` |
| Classification | `col-span-5` | `col-span-12` |
| Financials + Structure | `col-span-12` | `col-span-12` |
| Regulatory & Risk | `col-span-12` | `col-span-12` |

---

## Implementation Tasks

### Task 1: Refactor Grid Structure
**File:** `app/components/deal_form_component.py`

**Changes:**
1. Replace outer div with `rx.el.div` using `grid grid-cols-12 gap-4`
2. Update Identity card: `col-span-12 lg:col-span-7`
3. Update Classification card: `col-span-12 lg:col-span-5`
4. Merge Financials + Structure & Warrants into single card: `col-span-12`
   - Internal grid: 4 fields per row → `grid grid-cols-2 lg:grid-cols-4`
5. Regulatory & Risk remains `col-span-12` with `grid-cols-3 lg:grid-cols-6`

### Task 2: Reduce Vertical Padding
**Changes:**
- Section card padding: `p-4` → `p-3`
- Field margin-bottom: `mb-2` → `mb-1.5`
- Section header margin: `mb-3 pb-1.5` → `mb-2 pb-1`
- Input padding: `py-1.5` → `py-1`

### Task 3: Combine Financials + Structure Section
**Rationale:** Per user spec, these should be in a "single wide section with 4 fields per row"

**New Layout:**
```
Row 1: Pricing Date | Announce Date | Primary Shares | Secondary Shares
Row 2: Shares (M)   | Offer Price   | Warrants Min   | Warrants Strike
Row 3: Market Cap   | Offer USD     | Warrants Exp   | [empty]
Row 4: Gross Spread | Net Purchase  | PMI Date       | Fee %
```

### Task 4: Responsive Breakpoints
**Desktop (lg:1024px+):**
- 12-column grid with specified allocations
- All content visible without scrolling

**Mobile (<1024px):**
- Single column stack (`col-span-12`)
- Fields stack to 2-column within sections

---

## Code Changes Preview

### Main Form Structure
```python
rx.el.div(
    # 12-column grid container
    rx.el.div(
        # Top Row
        identity_card(),     # col-span-12 lg:col-span-7
        classification_card(), # col-span-12 lg:col-span-5
        
        # Middle Row (combined)
        financials_structure_card(), # col-span-12, 4-col internal grid
        
        # Bottom Row
        regulatory_card(),   # col-span-12, 6-col internal grid
        
        # Action Bar
        action_bar(),        # col-span-12
        
        class_name="grid grid-cols-12 gap-3",
    ),
)
```

---

## Acceptance Criteria
- [ ] Identity spans 7/12 columns on desktop
- [ ] Classification spans 5/12 columns on desktop  
- [ ] Financials + Structure combined with 4 fields/row
- [ ] Regulatory displays as horizontal 6-column strip
- [ ] All sections visible on 1080p without scrolling
- [ ] Graceful single-column stack on mobile
- [ ] Reduced padding for maximum density

---

## Risk Mitigation
- **Form validation**: Preserved from original `compact_form_field` component
- **Event handlers**: All `on_change`, `on_blur`, `on_submit` preserved
- **Edit mode detection**: `DealFormState.form_mode == "edit"` still works

---

## Estimated Effort
- **Implementation**: ~20 minutes
- **Testing**: ~5 minutes (browser verification)
