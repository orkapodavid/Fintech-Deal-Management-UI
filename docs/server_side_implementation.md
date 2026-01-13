# Server-Side Implementation Guide

This document serves as the blueprint for connecting the Fintech Deal Management UI to a real backend. The application is architected using a **UI -> State -> Service** pattern to ensure clean separation of concerns.

To implement the backend, you will primarily modify the classes in `app/services/`. The UI and State layers are already configured to consume these services.

## Architecture Overview

1.  **UI Layer** (`app/pages`, `app/components`): Triggers events (e.g., `on_click`, `on_mount`).
2.  **State Layer** (`app/states`): Handles business logic, input validation, and calls the Service layer.
3.  **Service Layer** (`app/services`): Abstract interface for data fetch/persistence. **This is where your implementations go.**

---

## Service Implementation Map

Use this table to audit your backend implementation. Every "Service Method" listed here must be fully implemented to support the UI.

| Feature Area | UI Action / Event | State Handler (`app/states`) | Service Method (`app/services`) | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Dashboard** | Page Load / Refresh | `DealState.load_data` | `DealService.get_deals()` | Fetch all active deals for the dashboard grid. |
| **Deal Management** | Delete Selected | `DealState.delete_selected_deals` | `DealService.delete_deal(id)` | Delete a specific deal by its unique ID. |
| **Deal Management** | Add New Deal | `DealState.submit_new_deal` | `DealService.save_deal(deal)` | Create a new deal record. |
| **Deal Management** | Edit/Update Deal | `DealState.approve_current_deal` | `DealService.save_deal(deal)` | Update an existing deal record (upsert). |
| **Review Flow** | Approve Deal | `DealState.approve_current_deal` | `DealService.save_deal(deal)` | Update deal status to `active` and save. |
| **Review Flow** | Reject Deal | `DealState.reject_current_deal` | `DealService.delete_deal(id)` | Delete the deal permanently. |
| **Alerts** | Sidebar Load | `AlertState.generate_alerts` | `AlertService.get_alerts()` | Fetch system alerts. |

---

## Required Service Signatures

### 1. DealService (`app/services/deal_service.py`)

Handles all persistence for Deal objects.

#### Data Model
Refer to `app/states/schema.py` -> `class Deal(rx.Base)` for the full schema.

#### Methods to Implement

```python
class DealService:
    def get_deals(self) -> List[Deal]:
        """
        Fetch all deals from the database.
        Returns: List of Deal objects.
        """
        # TODO: SELECT * FROM deals
        pass

    def get_deal_by_id(self, deal_id: str) -> Optional[Deal]:
        """
        Fetch a single deal by ID.
        Returns: Deal object or None.
        """
        # TODO: SELECT * FROM deals WHERE id = :deal_id
        pass

    def get_deal_by_ticker(self, ticker: str) -> Optional[Deal]:
        """
        Fetch a single deal by Ticker.
        Used for fallback lookup during imports or duplicates checks.
        """
        # TODO: SELECT * FROM deals WHERE ticker = :ticker
        pass

    def save_deal(self, deal: Deal) -> Deal:
        """
        Create or Update (Upsert) a deal.
        If deal.id exists, update. Else, insert.
        Returns: The saved Deal object (with updated ID/timestamps).
        """
        # TODO: INSERT OR UPDATE deals ...
        pass

    def delete_deal(self, deal_id: str) -> bool:
        """
        Delete a deal by ID.
        Returns: True if deleted, False if not found.
        """
        # TODO: DELETE FROM deals WHERE id = :deal_id
        pass
```

### 2. AlertService (`app/services/alert_service.py`)

Handles system notifications.

#### Data Model
Refer to `app/states/schema.py` -> `class Alert(rx.Base)`.

#### Methods to Implement

```python
class AlertService:
    def get_alerts(self) -> List[Alert]:
        """
        Fetch active alerts for the user/system.
        Returns: List of Alert objects.
        """
        # TODO: SELECT * FROM alerts WHERE dismissed = false
        pass
```

---

## Implementation Strategies

### Option A: Direct Replacement (Simpler)
Modify the existing files `app/services/deal_service.py` and `app/services/alert_service.py` directly. Remove the `Faker` logic and `_deals` lists, and replace them with your database calls (e.g., using `SQLAlchemy`, `psycopg2`, or `httpx` for APIs).

### Option B: Interface / Dependency Injection (Cleaner)
1.  Rename existing services to `MockDealService` / `MockAlertService`.
2.  Create new files `app/services/sql_deal_service.py`, etc.
3.  Update `app/states/deal_state.py` to import and instantiate your new service class.

```python
# app/states/deal_state.py
# from app.services.deal_service import DealService  <-- Remove
from app.services.sql_deal_service import SqlDealService as DealService # <-- Add
```
