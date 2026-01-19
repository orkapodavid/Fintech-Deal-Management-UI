# Task: Create an Input Form

## User Clarification Required

Before proceeding, please confirm or provide the following information:

1. **Entity Name**: What is this form for? (e.g., "User", "Trade", "Report")
2. **Form Purpose**: What does this form do? (e.g., "Create a new trade", "Edit user profile")
3. **Fields**: List all fields with:
   - Field name (e.g., `ticker`, `email`)
   - Field type (text, number, date, checkbox, select, textarea)
   - Required or optional
   - Validation rules (e.g., "must be positive", "2-10 chars", "percentage 0-100")
4. **Section Grouping**: How should fields be grouped? (e.g., "Identity", "Financials", "Settings")
5. **Cross-Field Validation**: Any rules that depend on multiple fields? (e.g., "end_date must be after start_date")
6. **Form Modes**: Does this form support multiple modes? (add/edit/review)

---

## Overview

This prompt guides the creation of a complete input form with:
- Pydantic model for data validation
- Form state management with validation feedback
- Responsive multi-column layout (optimized for wide screens, usable on mobile)

---

## Files to Create/Modify

### 1. Pydantic Model (Schema)
**File**: `app/states/shared/schema.py` or `app/states/{module}/types.py`

Define the data model with field validation:

```python
from typing import Optional, ClassVar
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
import re
import uuid


class {Entity}Status(str, Enum):
    """Status enum for the entity."""
    ACTIVE = "active"
    DRAFT = "draft"
    # Add more statuses as needed


class {Entity}(BaseModel):
    """Pydantic model for {Entity} with validation."""
    
    # ID field - auto-generated
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Required fields
    name: str  # Example required field
    
    # Optional fields with defaults
    description: Optional[str] = None
    amount: Optional[float] = None
    status: {Entity}Status = {Entity}Status.DRAFT
    
    # Timestamps
    created_at: str
    updated_at: str
    
    # Class-level constants for dropdowns
    STATUSES: ClassVar[list[str]] = ["active", "draft", "pending"]
    CATEGORIES: ClassVar[list[str]] = ["Category A", "Category B", "Category C"]

    # ===== Field Validators =====
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty and meets format requirements."""
        if not v:
            raise ValueError("Name is required")
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Name must be 2-100 characters")
        return v

    @field_validator("amount")
    @classmethod
    def validate_positive_amount(cls, v: Optional[float]) -> Optional[float]:
        """Validate amount is positive if provided."""
        if v is not None and v < 0:
            raise ValueError("Amount must be positive")
        return v

    @field_validator("date_field")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date is in YYYY-MM-DD format."""
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Invalid date format (YYYY-MM-DD)")
        return v

    @field_validator("percentage_field")
    @classmethod
    def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
        """Validate percentage is between 0-100."""
        if v is not None and not (0 <= v <= 100):
            raise ValueError("Percentage must be between 0-100")
        return v

    # ===== Cross-Field Validators =====
    
    @model_validator(mode="after")
    def validate_cross_fields(self) -> "{Entity}":
        """Validate fields that depend on each other."""
        # Example: end_date must be after start_date
        if self.start_date and self.end_date:
            s_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            e_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            if e_date < s_date:
                raise ValueError("End date cannot be before start date")
        
        # Example: conditional required field
        if self.is_enabled and not self.config_value:
            raise ValueError("Config value is required when enabled")
        
        return self
```

---

### 2. Form State
**File**: `app/states/{module}/{entity}_form_state.py`

Handles form data, validation state, and form lifecycle:

```python
import reflex as rx
import logging
from enum import Enum
from datetime import datetime
from pydantic import ValidationError
from app.states.shared.schema import {Entity}


class FormMode(str, Enum):
    ADD = "add"
    EDIT = "edit"
    REVIEW = "review"


class {Entity}FormState(rx.State):
    """State manager for {Entity} form with validation."""
    
    # Form state
    form_mode: FormMode = FormMode.ADD
    form_values: dict[str, str | int | float | bool | None] = {}
    validation_results: dict[str, dict[str, str | bool | None]] = {}
    
    # Form lifecycle
    is_dirty: bool = False
    is_submitting: bool = False
    touched_fields: list[str] = []
    form_key: int = 0  # Increment to force form remount

    # ===== Computed Vars =====
    
    @rx.var
    def has_errors(self) -> bool:
        """Check if form has any validation errors."""
        return any(
            not r.get("is_valid", True) for r in self.validation_results.values()
        )

    @rx.var
    def error_count(self) -> int:
        """Count total validation errors."""
        return sum(
            1 for r in self.validation_results.values() if not r.get("is_valid", True)
        )

    @rx.var
    def field_errors(self) -> dict[str, str]:
        """Returns dict of field_name -> error_message for invalid fields."""
        errors = {}
        for field, result in self.validation_results.items():
            if not result.get("is_valid", True) and result.get("error_message"):
                errors[field] = result["error_message"]
        return errors

    @rx.var
    def can_submit(self) -> bool:
        """Check if form can be submitted."""
        is_valid = not self.has_errors
        has_required = bool(
            self.form_values.get("required_field_1")
            and self.form_values.get("required_field_2")
        )
        return is_valid and not self.is_submitting and has_required

    # ===== Event Handlers =====
    
    @rx.event
    def set_field_value(self, field: str, value: str | int | float | bool | None):
        """Set field value and trigger validation."""
        self.form_values[field] = value
        self.is_dirty = True
        self._validate_single_field(field)
        
        # Define cross-field triggers (when one field changes, validate related fields)
        cross_triggers = {
            "start_date": ["end_date"],
            "is_enabled": ["config_value"],
            # Add more as needed
        }
        if field in cross_triggers:
            for related in cross_triggers[field]:
                self._validate_single_field(related)

    @rx.event
    def touch_field(self, field: str):
        """Mark field as touched (for showing validation on blur)."""
        if field not in self.touched_fields:
            self.touched_fields.append(field)
            self._validate_single_field(field)

    def _validate_single_field(self, field: str):
        """Internal helper to validate a single field."""
        self.validate_form()

    @rx.event
    def validate_form(self):
        """Validate entire form using Pydantic model."""
        results = {}
        
        # Skip validation if required fields are empty (user just started)
        if not self.form_values.get("required_field_1"):
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
            self.validation_results = results
            return
        
        try:
            # Prepare data for Pydantic
            data = {}
            for k, v in self.form_values.items():
                # Convert empty strings to None for optional fields
                if v == "" and k not in ["required_field_1", "required_field_2"]:
                    data[k] = None
                else:
                    data[k] = v
            
            # Validate with Pydantic
            {Entity}(**{**{"created_at": "", "updated_at": ""}, **data})
            
            # All valid
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
                
        except ValidationError as e:
            logging.exception(f"Validation error: {e}")
            
            # Mark all fields valid first
            for field in self.form_values.keys():
                results[field] = {"is_valid": True, "error_message": None}
            
            # Then set error fields
            for error in e.errors():
                field_name = error["loc"][0]
                msg = error["msg"]
                if msg.startswith("Value error, "):
                    msg = msg.replace("Value error, ", "")
                results[str(field_name)] = {"is_valid": False, "error_message": msg}
        
        self.validation_results = results
        if not self.touched_fields:
            self.touched_fields = list(self.form_values.keys())

    @rx.event
    def reset_form(self):
        """Reset form to initial state."""
        self.form_values = {}
        self.validation_results = {}
        self.touched_fields = []
        self.is_dirty = False
        self.is_submitting = False
        self.form_mode = FormMode.ADD
        self.form_key += 1  # Force form remount

    @rx.event
    def on_page_load(self):
        """Handle page load - check mode from query params."""
        mode = self.router.page.params.get("mode", "add")
        if mode != "edit":
            self.reset_form()

    @rx.event
    def load_for_edit(self, entity: {Entity}, mode: str = "edit"):
        """Load existing entity data for editing."""
        self.reset_form()
        processed_values = entity.dict()
        
        # Convert datetime and enum values to strings
        for k, v in processed_values.items():
            if isinstance(v, datetime):
                processed_values[k] = v.isoformat()
            elif isinstance(v, Enum):
                processed_values[k] = v.value
        
        self.form_values = processed_values
        self.form_mode = FormMode(mode)
        self.validate_form()
        self.touched_fields = []

    @rx.event
    def set_form_mode(self, mode: str):
        """Set form mode (add/edit/review)."""
        try:
            self.form_mode = FormMode(mode)
        except ValueError as e:
            logging.exception(f"Error setting form mode: {e}")
```

---

### 3. Form Component
**File**: `app/components/{module}/{entity}_form_component.py`

Reusable form UI with responsive grid layout:

```python
import reflex as rx
from app.states.{module}.{entity}_form_state import {Entity}FormState
from app.states.{module}.{module}_state import {Module}State


def form_field(
    label: str,
    key: str,
    type_: str = "text",
    placeholder: str = "",
    required: bool = False,
) -> rx.Component:
    """
    Reusable form field with validation feedback.
    
    Args:
        label: Field label text
        key: Field key in form_values
        type_: Input type (text, number, date, email, etc.)
        placeholder: Placeholder text
        required: Whether field is required
    """
    error = {Entity}FormState.field_errors[key]
    is_touched = {Entity}FormState.touched_fields.contains(key)
    raw_has_error = ~{Entity}FormState.validation_results[key]["is_valid"]
    has_error = is_touched & raw_has_error
    
    # Dynamic border styling based on validation state
    border_class = rx.cond(
        has_error,
        "border-red-300 focus:border-red-500 focus:ring-red-500 bg-red-50",
        "border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white",
    )
    
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label,
                class_name="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.input(
                type=type_,
                name=key,
                key=f"{key}_{{Entity}FormState.form_key}",
                default_value={Entity}FormState.form_values[key].to(str),
                on_change=lambda v: {Entity}FormState.set_field_value(key, v),
                on_blur=lambda: {Entity}FormState.touch_field(key),
                placeholder=placeholder,
                class_name=f"block w-full rounded-md py-2 text-gray-900 shadow-sm ring-1 ring-inset {border_class} placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6 pl-3 transition-colors",
            ),
            rx.cond(
                has_error,
                rx.icon(
                    "circle-alert",
                    class_name="absolute right-3 top-2.5 text-red-500 w-5 h-5",
                ),
                None,
            ),
            class_name="relative mt-1",
        ),
        rx.cond(
            has_error,
            rx.el.p(error, class_name="mt-1 text-xs text-red-600 font-medium"),
            None,
        ),
        class_name="mb-4",
    )


def compact_form_field(
    label: str,
    key: str,
    type_: str = "text",
    placeholder: str = "",
) -> rx.Component:
    """Compact form field for dense multi-column layouts."""
    error = {Entity}FormState.field_errors[key]
    is_touched = {Entity}FormState.touched_fields.contains(key)
    raw_has_error = ~{Entity}FormState.validation_results[key]["is_valid"]
    has_error = is_touched & raw_has_error
    
    border_class = rx.cond(
        has_error,
        "border-red-300 focus:border-red-500 focus:ring-red-500 bg-red-50",
        "border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white",
    )
    
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-0.5",
        ),
        rx.el.div(
            rx.el.input(
                type=type_,
                name=key,
                key=f"{key}_{{Entity}FormState.form_key}",
                default_value={Entity}FormState.form_values[key].to(str),
                on_change=lambda v: {Entity}FormState.set_field_value(key, v),
                on_blur=lambda: {Entity}FormState.touch_field(key),
                placeholder=placeholder,
                class_name=f"block w-full rounded py-1.5 text-gray-900 shadow-sm ring-1 ring-inset {border_class} placeholder:text-gray-400 focus:ring-2 focus:ring-inset text-sm pl-2 transition-colors",
            ),
            rx.cond(
                has_error,
                rx.icon(
                    "circle-alert",
                    class_name="absolute right-2 top-1.5 text-red-500 w-4 h-4",
                ),
                None,
            ),
            class_name="relative",
        ),
        rx.cond(
            has_error,
            rx.el.p(error, class_name="mt-0.5 text-[10px] text-red-600 font-medium"),
            None,
        ),
        class_name="mb-2",
    )


def section_header(icon: str, title: str) -> rx.Component:
    """Section header for grouping form fields."""
    return rx.el.div(
        rx.icon(icon, class_name="w-3.5 h-3.5 text-blue-500 mr-1.5"),
        rx.el.h3(
            title,
            class_name="text-xs font-semibold text-gray-900 uppercase tracking-wide",
        ),
        class_name="flex items-center mb-3 pb-1.5 border-b border-gray-100",
    )


def checkbox_field(label: str, key: str) -> rx.Component:
    """Checkbox input field."""
    return rx.el.label(
        rx.el.input(
            type="checkbox",
            name=key,
            key=f"{key}_{{Entity}FormState.form_key}",
            default_checked={Entity}FormState.form_values[key].to(bool),
            on_change=lambda v: {Entity}FormState.set_field_value(key, v),
            class_name="rounded text-blue-600 focus:ring-blue-500 mr-1.5 w-3.5 h-3.5",
        ),
        label,
        class_name="text-xs text-gray-600 flex items-center",
    )


def textarea_field(label: str, key: str, placeholder: str = "") -> rx.Component:
    """Textarea field for longer text content."""
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1",
        ),
        rx.el.textarea(
            name=key,
            key=f"{key}_{{Entity}FormState.form_key}",
            default_value={Entity}FormState.form_values[key].to(str),
            on_change=lambda v: {Entity}FormState.set_field_value(key, v),
            placeholder=placeholder,
            class_name="w-full h-40 rounded border-gray-300 py-1 px-2 text-gray-900 shadow-sm ring-1 ring-inset focus:ring-2 focus:ring-inset focus:ring-blue-500 text-xs resize-none",
        ),
    )


def {entity}_form_component() -> rx.Component:
    """
    Main form component with responsive Bento Box layout.
    
    Layout uses CSS Grid with 12-column system:
    - Desktop (lg:): Full multi-column layout
    - Tablet (md:): Reduced columns  
    - Mobile: Single column stack
    """
    return rx.el.div(
        rx.el.form(
            # ===== Section 1: Primary Info (7-col) + Secondary Info (5-col) =====
            rx.el.div(
                # Primary section - 7/12 columns on desktop
                rx.el.div(
                    section_header("building-2", "Primary Information"),
                    rx.el.div(
                        # Use responsive grid: 2 cols on mobile, 3 cols on desktop
                        compact_form_field("Field 1", "field_1", placeholder="Value"),
                        compact_form_field("Field 2", "field_2", placeholder="Value"),
                        compact_form_field("Field 3", "field_3", type_="number"),
                        class_name="grid grid-cols-2 lg:grid-cols-3 gap-x-3 gap-y-1",
                    ),
                    compact_form_field("Full Width Field", "full_width_field"),
                    class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 h-full col-span-12 lg:col-span-7",
                ),
                # Secondary section - 5/12 columns on desktop
                rx.el.div(
                    section_header("tag", "Secondary Information"),
                    rx.el.div(
                        compact_form_field("Category", "category"),
                        compact_form_field("Status", "status"),
                        class_name="grid grid-cols-2 gap-x-3 gap-y-1",
                    ),
                    # Checkbox group
                    rx.el.div(
                        checkbox_field("Option A", "option_a"),
                        checkbox_field("Option B", "option_b"),
                        checkbox_field("Option C", "option_c"),
                        class_name="flex gap-3 mt-2 pt-2 border-t border-gray-50",
                    ),
                    # Notes textarea
                    textarea_field("Notes", "notes", placeholder="Enter notes..."),
                    class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 h-full col-span-12 lg:col-span-5",
                ),
                class_name="grid grid-cols-12 gap-3 mb-3",
            ),
            
            # ===== Section 2: Dense Data Grid (full width) =====
            rx.el.div(
                section_header("dollar-sign", "Details"),
                rx.el.div(
                    # 6-column grid on desktop, 3 on tablet, 2 on mobile
                    compact_form_field("Date 1", "date_1", type_="date"),
                    compact_form_field("Date 2", "date_2", type_="date"),
                    compact_form_field("Amount 1", "amount_1", type_="number"),
                    compact_form_field("Amount 2", "amount_2", type_="number"),
                    compact_form_field("Percentage", "percentage", type_="number"),
                    compact_form_field("Value", "value", type_="number"),
                    class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-3 gap-y-1",
                ),
                class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 mb-3",
            ),
            
            # ===== Action Bar =====
            rx.el.div(
                rx.el.button(
                    "Clear",
                    type="button",
                    on_click={Entity}FormState.reset_form,
                    class_name="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors text-sm mr-2",
                ),
                rx.el.button(
                    rx.cond(
                        {Entity}FormState.form_mode == "edit",
                        "Update",
                        "Submit",
                    ),
                    type="submit",
                    disabled=~{Entity}FormState.can_submit,
                    class_name="px-4 py-1.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                ),
                class_name="flex items-center justify-end bg-white p-3 rounded-lg shadow-sm border border-gray-100",
            ),
            on_submit={Module}State.submit_{entity},
            reset_on_submit=True,
        ),
        key={Entity}FormState.form_key,
    )
```

---

## Responsive Grid Patterns

### Desktop (lg:) - Wide Screen Optimized
- Use 12-column grid system
- Dense layouts with 6 columns for data-heavy sections
- 7+5 split for primary/secondary sections

### Tablet (md:) - Medium Screen
- Reduce to 3 columns for data grids
- Maintain 2-column layouts for form sections

### Mobile - Single Column Stack
- All sections stack vertically
- 2-column grid for compact fields
- Full-width inputs for important fields

### Grid Classes Reference
```css
/* 6-column dense grid (desktop) → 3 (tablet) → 2 (mobile) */
grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-3 gap-y-1

/* 3-column grid (desktop) → 2 (mobile) */
grid grid-cols-2 lg:grid-cols-3 gap-x-3 gap-y-1

/* 12-column grid for major sections */
grid grid-cols-12 gap-3 mb-3

/* Column spans */
col-span-12 lg:col-span-7   /* 7/12 on desktop, full on mobile */
col-span-12 lg:col-span-5   /* 5/12 on desktop, full on mobile */
```

---

## Verification Checklist

- [ ] Pydantic model created with all validators
- [ ] Form state created with validation logic
- [ ] Form component created with responsive layout
- [ ] Form field components (`form_field`, `compact_form_field`) work correctly
- [ ] Cross-field validation triggers on related field changes
- [ ] Error messages display only after field is touched
- [ ] Form can be reset and re-initialized
- [ ] Form loads correctly for edit mode
- [ ] Submit button disabled until form is valid
- [ ] Mobile layout is usable (test at 375px width)
- [ ] Desktop layout uses full width efficiently

---

## Common Validation Patterns

### Required Field
```python
@field_validator("name")
@classmethod
def validate_name(cls, v: str) -> str:
    if not v:
        raise ValueError("Name is required")
    return v
```

### Positive Number
```python
@field_validator("amount")
@classmethod
def validate_positive(cls, v: Optional[float]) -> Optional[float]:
    if v is not None and v < 0:
        raise ValueError("Value must be positive")
    return v
```

### Percentage (0-100)
```python
@field_validator("rate")
@classmethod
def validate_percentage(cls, v: Optional[float]) -> Optional[float]:
    if v is not None and not (0 <= v <= 100):
        raise ValueError("Percentage must be between 0-100")
    return v
```

### Date Format
```python
@field_validator("date_field")
@classmethod
def validate_date(cls, v: Optional[str]) -> Optional[str]:
    if v:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format (YYYY-MM-DD)")
    return v
```

### Enum/Choice Validation
```python
@field_validator("category")
@classmethod
def validate_category(cls, v: Optional[str]) -> Optional[str]:
    if v and v not in cls.CATEGORIES:
        raise ValueError(f"Must be one of: {', '.join(cls.CATEGORIES)}")
    return v
```

### Regex Pattern
```python
@field_validator("ticker")
@classmethod
def validate_ticker(cls, v: str) -> str:
    if not re.match("^[A-Z0-9]{2,10}$", v):
        raise ValueError("Must be 2-10 uppercase alphanumeric characters")
    return v
```

### Cross-Field: Date Order
```python
@model_validator(mode="after")
def validate_dates(self) -> "Entity":
    if self.start_date and self.end_date:
        start = datetime.strptime(self.start_date, "%Y-%m-%d")
        end = datetime.strptime(self.end_date, "%Y-%m-%d")
        if end < start:
            raise ValueError("End date cannot be before start date")
    return self
```

### Cross-Field: Conditional Required
```python
@model_validator(mode="after")
def validate_conditional(self) -> "Entity":
    if self.is_enabled and not self.config_value:
        raise ValueError("Config value required when enabled")
    return self
```
