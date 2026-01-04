# HDP Deal Management App - Refactoring Plan

## Phase 1: Implement Persistent Storage with SQLModel ✅
- [x] Configure SQLite database in rxconfig.py with proper db_url
- [x] Update Deal and Alert models to use rx.Model base class for database integration
- [x] Refactor DealState to use database sessions (rx.session) for CRUD operations
- [x] Replace in-memory list operations with session.add(), session.exec() queries
- [x] Add database initialization on app startup with sample data seeding

---

## Phase 2: Refactor Validation to Pydantic & Clean Up Code ✅
- [x] Move validation rules from ValidationService into Deal model using Pydantic @field_validator decorators
- [x] Add cross-field validation using @model_validator for complex rules (dates, shares totals)
- [x] Update DealFormState to use model-based validation instead of ValidationService
- [x] Remove app/states/validation.py file after migration
- [x] Remove PyGithub from requirements.txt (unused dependency)
- [x] Delete app/components/deal_form.py (superseded by deal_form_component.py)

---

## Phase 3: Decouple Form Component & Add Testing ✅
- [x] Refactor deal_form_component.py to accept state/handlers as parameters
- [x] Create generic form field factory that works with any state class
- [x] Create tests/ directory structure with pytest configuration
- [x] Add unit tests for Deal model validation (ticker, structure, dates, numeric fields)
- [x] Add integration tests for DealState CRUD operations with database