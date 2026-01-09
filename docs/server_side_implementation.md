# Server-Side Implementation Guide

This document outlines how to replace the mock memory-based services with real server-side implementations.

## Overview

The application currently uses a service layer pattern in `app/services/` to abstract data access. The current implementations (`DealService`, `AlertService`) store data in memory and generate fake data on startup.

To connect to a real backend (Database, API, etc.), you should replace the logic in these service classes.

## DealService (`app/services/deal_service.py`)

Currently, this service manages a list of `Deal` objects in memory.

### Steps to Replace:

1.  **Database Connection**: Initialize your database connection (SQLAlchemy, AsyncPG, etc.) in `__init__` or imported from a `db.py` module.
2.  **`get_deals()`**: Replace the in-memory list return with a database query.
    ```python
    def get_deals(self) -> List[Deal]:
        # Example: return session.query(DealModel).all()
        ...
    ```
3.  **`save_deal(deal)`**: Implement upsert logic against your database.
4.  **`delete_deal(deal_id)`**: Implement delete logic.

## AlertService (`app/services/alert_service.py`)

Currently generates random alerts.

### Steps to Replace:

1.  **`get_alerts()`**: Fetch real alerts from your monitoring system or database.

## Dependency Injection

If you plan to have multiple implementations (e.g., `MockDealService` vs `SqlDealService`), consider using dependency injection or a factory pattern to instantiate the correct service in `DealState`.

For now, modifying the methods in the existing classes is the simplest approach.
