# Backend & API Productionization To-Do List

This document outlines all tasks required to fully productionize the Fintech Deal Management UI with proper backend and API handling. The current application uses in-memory mock data (via `Faker`) and has no persistent storage or real API integration.

---

## Current State Summary

| Area | Current Status | Production Ready |
|------|----------------|------------------|
| **Frontend UI** | ✅ Complete | ✅ Yes |
| **State Management** | ✅ Complete | ✅ Yes |
| **Data Services** | ⚠️ Mock Data | ❌ No |
| **Database** | ❌ None | ❌ No |
| **Authentication** | ❌ None | ❌ No |
| **API Layer** | ❌ None | ❌ No |
| **Testing** | ❌ None | ❌ No |
| **CI/CD** | ❌ None | ❌ No |
| **Documentation** | ⚠️ Partial | ⚠️ Partial |

---

## Phase 1: Database Layer

### 1.1 Database Setup
- [ ] Choose database technology (recommended: PostgreSQL or MS SQL Server)
- [ ] Create database schema from `app/states/shared/schema.py`
- [ ] Write SQL migration scripts for:
  - [ ] `deals` table (~40 columns per `Deal` model)
  - [ ] `alerts` table (system notifications)
  - [ ] `users` table (for authentication)
  - [ ] `audit_log` table (for change tracking)

### 1.2 ORM/Data Access Layer
- [ ] Install database driver (`psycopg2`, `pymssql`, or `sqlalchemy`)
- [ ] Create `app/database/` directory structure:
  ```
  app/database/
  ├── __init__.py
  ├── connection.py      # Connection pool management
  ├── models.py          # SQLAlchemy or raw models
  └── migrations/        # Alembic or manual SQL scripts
  ```
- [ ] Implement connection pooling for production
- [ ] Add database URL to environment configuration

---

## Phase 2: Service Layer Refactoring

### 2.1 DealService (`app/services/deals/deal_service.py`)
Replace mock `Faker` implementation with real database calls:

- [ ] **`get_deals() -> List[Deal]`**
  - Remove `_generate_fake_data()` method
  - Implement: `SELECT * FROM deals`
  - Add pagination support (`LIMIT/OFFSET`)
  - Add filtering support (status, date range, etc.)

- [ ] **`get_deal_by_id(deal_id: str) -> Optional[Deal]`**
  - Implement: `SELECT * FROM deals WHERE id = ?`

- [ ] **`get_deal_by_ticker(ticker: str) -> Optional[Deal]`**
  - Implement: `SELECT * FROM deals WHERE ticker = ?`

- [ ] **`save_deal(deal: Deal) -> Deal`**
  - Implement upsert logic (INSERT ON CONFLICT or UPDATE)
  - Update `updated_at` timestamp
  - Return deal with generated ID

- [ ] **`delete_deal(deal_id: str) -> bool`**
  - Implement: `DELETE FROM deals WHERE id = ?`
  - Consider soft-delete (add `deleted_at` column)

### 2.2 AlertService (`app/services/alerts/alert_service.py`)
Replace mock random alerts with real storage:

- [ ] **`get_alerts() -> List[Alert]`**
  - Implement: `SELECT * FROM alerts WHERE is_dismissed = false`
  - Add user filtering if multi-tenant

- [ ] **`dismiss_alert(alert_id: int) -> bool`**
  - Implement: `UPDATE alerts SET is_dismissed = true WHERE id = ?`

- [ ] **`create_alert(alert: Alert) -> Alert`**
  - Implement alert creation for system events

### 2.3 New Services to Create

- [ ] **UserService** (`app/services/users/user_service.py`)
  - `authenticate(username, password)`
  - `get_user_by_id(user_id)`
  - `create_user(user_data)`

- [ ] **AuditService** (`app/services/audit/audit_service.py`)
  - `log_action(user_id, action, entity_type, entity_id, changes)`
  - `get_audit_trail(entity_type, entity_id)`

---

## Phase 3: API Layer

### 3.1 REST API Endpoints
Create `app/api/` directory for FastAPI or similar:

```
app/api/
├── __init__.py
├── routes/
│   ├── deals.py        # /api/deals/*
│   ├── alerts.py       # /api/alerts/*
│   └── auth.py         # /api/auth/*
├── schemas/            # Pydantic request/response models
│   ├── deal.py
│   ├── alert.py
│   └── auth.py
└── dependencies.py     # Auth, DB session injection
```

### 3.2 Deal Endpoints
- [ ] `GET /api/deals` - List deals with filtering/pagination
- [ ] `GET /api/deals/{id}` - Get single deal
- [ ] `POST /api/deals` - Create new deal
- [ ] `PUT /api/deals/{id}` - Update deal
- [ ] `DELETE /api/deals/{id}` - Delete deal
- [ ] `GET /api/deals/export` - Export as CSV

### 3.3 Alert Endpoints
- [ ] `GET /api/alerts` - Get active alerts
- [ ] `POST /api/alerts/{id}/dismiss` - Dismiss alert

### 3.4 Auth Endpoints
- [ ] `POST /api/auth/login` - User login
- [ ] `POST /api/auth/logout` - User logout
- [ ] `GET /api/auth/me` - Get current user

---

## Phase 4: Authentication & Authorization

### 4.1 Authentication Implementation
- [ ] Choose authentication strategy:
  - Option A: Session-based (simpler for Reflex)
  - Option B: JWT tokens (stateless)
  - Option C: OAuth2/SSO integration
- [ ] Implement login page component
- [ ] Implement protected route wrapper
- [ ] Add user session state management

### 4.2 Authorization
- [ ] Define user roles (admin, reviewer, analyst)
- [ ] Implement role-based access control (RBAC)
- [ ] Add permission checks to service methods
- [ ] Hide UI elements based on permissions

### 4.3 Security Hardening
- [ ] Password hashing (bcrypt/argon2)
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input sanitization
- [ ] SQL injection prevention (parameterized queries)

---

## Phase 5: Testing

### 5.1 Unit Tests
Create `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures
├── test_services/
│   ├── test_deal_service.py
│   └── test_alert_service.py
├── test_api/
│   ├── test_deals_api.py
│   └── test_auth_api.py
└── test_states/
    └── test_deal_state.py
```

- [ ] DealService CRUD tests
- [ ] AlertService tests
- [ ] Validation logic tests
- [ ] API endpoint tests (with TestClient)

### 5.2 Integration Tests
- [ ] Database connection tests
- [ ] End-to-end workflow tests
- [ ] Authentication flow tests

### 5.3 Browser/E2E Tests
- [ ] Playwright or Selenium test setup
- [ ] Deal list page tests
- [ ] Add deal form tests
- [ ] Review workflow tests

---

## Phase 6: Configuration & Environment

### 6.1 Environment Configuration
- [ ] Create `.env.example` file
- [ ] Update `app/config.py` for environment-based config:
  ```python
  DATABASE_URL = os.getenv("DATABASE_URL")
  SECRET_KEY = os.getenv("SECRET_KEY")
  DEBUG = os.getenv("DEBUG", "false").lower() == "true"
  ```
- [ ] Add production/staging/development profiles

### 6.2 Secrets Management
- [ ] Document required secrets:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `API_KEYS` (if any external APIs)
- [ ] Integrate with secrets manager (Azure Key Vault, AWS Secrets Manager)

---

## Phase 7: Error Handling & Logging

### 7.1 Centralized Error Handling
- [ ] Create `app/exceptions.py` with custom exceptions:
  - `DealNotFoundError`
  - `ValidationError`
  - `AuthenticationError`
  - `AuthorizationError`
- [ ] Add global exception handlers
- [ ] Standardize error response format

### 7.2 Logging
- [ ] Configure structured logging (JSON format for production)
- [ ] Add request/response logging middleware
- [ ] Implement audit logging for sensitive operations
- [ ] Integrate with log aggregation (ELK, CloudWatch, etc.)

---

## Phase 8: CI/CD & Deployment

### 8.1 CI Pipeline
- [ ] Create `.github/workflows/ci.yml`:
  - Run linting (ruff)
  - Run type checking (mypy)
  - Run tests (pytest)
  - Build checks

### 8.2 Deployment Pipeline
- [ ] Create deployment workflow for:
  - Staging environment
  - Production environment
- [ ] Database migration automation
- [ ] Health check endpoints

### 8.3 Infrastructure
- [ ] Document deployment architecture
- [ ] Create IIS deployment script (see existing `deploy_update.ps1`)
- [ ] Container option (Dockerfile)

---

## Phase 9: External Integrations

### 9.1 Document Ingestion (Add Deal Page)
The UI shows "Upload PDF/DOCX" functionality - implement backend:
- [ ] File upload endpoint
- [ ] Document parsing service (extract deal data from PDFs)
- [ ] OCR integration (if needed for scanned documents)
- [ ] AI/ML integration for data extraction

### 9.2 Bloomberg Integration (if applicable)
- [ ] Ticker validation API
- [ ] Market data enrichment
- [ ] Real-time pricing feeds

---

## Phase 10: Documentation Updates

### 10.1 API Documentation
- [ ] OpenAPI/Swagger documentation
- [ ] API usage examples
- [ ] Authentication guide

### 10.2 Deployment Documentation
- [ ] Update `docs/setup.md` with database setup
- [ ] Production deployment guide
- [ ] Environment configuration guide

### 10.3 Developer Documentation
- [ ] Update `AGENTS.md` with new architecture
- [ ] Service layer documentation
- [ ] Testing guide

---

## Quick Reference: File Changes Required

| File | Change Type | Description |
|------|-------------|-------------|
| `app/services/deals/deal_service.py` | **MAJOR** | Replace Faker with DB calls |
| `app/services/alerts/alert_service.py` | **MAJOR** | Replace random data with DB calls |
| `app/database/__init__.py` | **NEW** | Database connection module |
| `app/api/routes/deals.py` | **NEW** | REST API endpoints |
| `app/api/routes/auth.py` | **NEW** | Authentication endpoints |
| `app/config.py` | **MODIFY** | Add database/auth config |
| `rxconfig.py` | **MODIFY** | Add API endpoint config |
| `tests/` | **NEW** | Complete test suite |
| `.env.example` | **NEW** | Environment template |

---

## Priority Order

1. ⭐ **Phase 1** - Database Setup (blocks everything else)
2. ⭐ **Phase 2** - Service Refactoring (enables persistence)
3. **Phase 4** - Authentication (security requirement)
4. **Phase 5** - Testing (quality gate)
5. **Phase 3** - API Layer (optional if Reflex-only)
6. **Phase 6-8** - Configuration, Logging, CI/CD
7. **Phase 9-10** - Integrations, Documentation
