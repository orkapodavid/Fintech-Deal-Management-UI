# Data Schema & API

This document details the data models and validation rules used in the application.

## Data Models

### Deal (`app/states/schema.py`)

Represents a financial deal.

| Field | Type | Description |
| :--- | :--- | :--- |
| `ticker` | `str` | **Primary Key**. 2-10 uppercase alphanumeric characters. |
| `structure` | `str` | Type of deal (e.g., IPO, M&A). Required. |
| `company_name` | `str` | Name of the company involved. |
| `status` | `DealStatus` | Current state: `active`, `pending_review`, `draft`. |
| `shares_amount` | `float` | Number of shares (in millions). |
| `offering_price` | `float` | Price per share. |
| `pricing_date` | `str` | Date of pricing (ISO format). |
| `announce_date` | `str` | Date of announcement (ISO format). |
| `flag_bought` | `bool` | "Bought Deal" flag. |
| `created_at` | `datetime` | Creation timestamp. |

*(See `app/states/schema.py` for the full list of ~40 fields)*

### Alert (`app/states/schema.py`)

Represents a system notification.

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `int` | **Primary Key**. |
| `severity` | `str` | Level: `critical`, `warning`, `system`. |
| `title` | `str` | Alert title. |
| `message` | `str` | Detailed message. |
| `deal_ticker` | `str` | Foreign key to `Deal.ticker` (optional). |

## Validation Rules

Validation is handled by `ValidationService` in `app/states/validation.py`.

### Critical Rules

1.  **Ticker**: Must be unique, 2-10 chars, uppercase alphanumeric.
2.  **Structure**: Must be one of `["IPO", "M&A", "Spin-off", "Follow-on", "Convertible"]`.
3.  **Dates**: `Pricing Date` cannot be before `Announce Date`.
4.  **Bought Deals**: If `flag_bought` is set, `offering_price` is mandatory.
5.  **Warrants**: If `warrants_min` > 0, then `warrants_strike` and `warrants_exp` are required.
6.  **Numeric Sanity**:
    *   Shares, Price, Market Cap must be positive.
    *   Shares Amount > 1000 triggers a "Check units" warning (expects millions).
    *   Percentages (Fee, Inst Own) must be 0-100.

### Cross-Field Validation

*   **Total Shares Mismatch**: Warning if `shares_amount` != `primary_shares` + `secondary_shares` (tolerance 1%).
