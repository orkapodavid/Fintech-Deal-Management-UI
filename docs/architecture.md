# Project Overview & Architecture

## Overview

The Deal Management App is a Reflex-based full-stack application designed for managing financial deals. Key features include:
*   **Deal Pipeline**: View and filter a list of active and drafted deals (`/deals`).
*   **Add Deal Flow**: A comprehensive multi-step form for inputting deal details (`/add`).
*   **Review Flow**: Interface for reviewing, approving, or rejecting pending deals (`/review`).
*   **Alerts**: Real-time simulated system alerts (`AlertState`).

## Directory Structure

*   **`app/app.py`**: The entry point. Defines the app instance, layout, and routing (`/`, `/deals`, `/add`, `/review`).
*   **`app/states/`**: Contains the business logic and state management.
    *   `schema.py`: SQLModel definitions for `Deal` and `Alert`.
    *   `deal_state.py`: Global application state (list of deals, filtering, pagination).
    *   `deal_form_state.py`: Local state for form handling (validation, field updates).
    *   `validation.py`: Custom `ValidationService` logic.
    *   `alert_state.py`: Manages system alerts.
*   **`app/components/`**: Reusable UI parts.
    *   `deal_form_component.py`: The main form UI, tightly coupled with `DealFormState`.
    *   `navbar.py`: Main navigation bar.
    *   `alert_sidebar.py`: Sidebar for displaying alerts.
*   **`app/pages/`**: Page-level components.
    *   `deals_page.py`: The dashboard/list view.
    *   `add_page.py`: Wrapper for the add deal form.
    *   `review_page.py`: Wrapper for the review process.

## State Management Pattern

The app uses a split-state architecture:

1.  **Global Data (`DealState`)**:
    *   Holds the "source of truth" list of deals (`self.deals`).
    *   Manages "view" logic like pagination (`current_page`), filtering (`search_query`), and selection.
    *   *Note*: Currently generates fake data on `load_data` if the list is empty.

2.  **Form/Interaction Data (`DealFormState`)**:
    *   Manages temporary form state (`form_values`, `is_dirty`, `touched_fields`).
    *   Handles validation logic via `ValidationService`.
    *   Used by both the "Add" and "Review" pages but resets context via `load_deal_for_edit`.

## Data Flow & Validation

1.  **Form Entry**: User types in `deal_form_component.py`.
2.  **State Update**: `on_change` triggers `DealFormState.set_field_value`.
3.  **Validation**:
    *   Immediate field-level validation runs on change.
    *   `ValidationService` (in `validation.py`) checks rules (regex, ranges, cross-field logic like `pricing_date` vs `announce_date`).
    *   Errors are stored in `DealFormState.validation_results` and reflected in the UI.
4.  **Submission**:
    *   `DealState.submit_new_deal` collects data from `DealFormState`.
    *   Data is appended to `DealState.deals` (in-memory).
