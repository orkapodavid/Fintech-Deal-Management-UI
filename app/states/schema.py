import reflex as rx
from typing import Optional, ClassVar, TypedDict
from enum import Enum
from pydantic import field_validator, model_validator, BaseModel
from datetime import datetime
import re
import logging


class DealStatus(str, Enum):
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"
    DRAFT = "draft"


class Deal(BaseModel):
    ticker: str
    structure: str
    concurrent: Optional[str] = None
    id_bb_global: Optional[str] = None
    id_sedol1: Optional[str] = None
    action_id: Optional[int] = None
    flag_bought: bool = False
    flag_clean_up: bool = False
    flag_top_up: bool = False
    pricing_date: Optional[str] = None
    announce_date: Optional[str] = None
    pmi_date: Optional[str] = None
    first_trade_date: Optional[str] = None
    inst_own_date: Optional[str] = None
    shares_amount: Optional[float] = None
    offering_price: Optional[float] = None
    price_on_pricing_date: Optional[float] = None
    vol_on_pricing_date: Optional[int] = None
    offer_price_usd: Optional[float] = None
    market_cap: Optional[float] = None
    fx_rate: Optional[float] = None
    gross_spread: Optional[float] = None
    net_purchase_price: Optional[float] = None
    fee_percent: Optional[float] = None
    reported_shares: Optional[float] = None
    bbg_shares: Optional[float] = None
    primary_shares: Optional[float] = None
    secondary_shares: Optional[float] = None
    eqy_sh_out: Optional[float] = None
    eqy_float: Optional[float] = None
    inst_own_pct: Optional[float] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    bics_level: Optional[str] = None
    company_name: Optional[str] = None
    deal_description: Optional[str] = None
    avg_volume: Optional[float] = None
    avg_daily_val: Optional[float] = None
    vix: Optional[float] = None
    vol_90_day: Optional[str] = None
    short_int: Optional[float] = None
    cdr_exch_code: Optional[str] = None
    reg_id: Optional[str] = None
    warrants_min: Optional[int] = None
    warrants_strike: Optional[float] = None
    warrants_exp: Optional[str] = None
    status: DealStatus = DealStatus.DRAFT
    ai_confidence_score: int = 100
    source_file: Optional[str] = None
    created_at: str
    updated_at: str
    STRUCTURES: ClassVar[list[str]] = [
        "IPO",
        "M&A",
        "Spin-off",
        "Follow-on",
        "Convertible",
    ]
    SECTORS: ClassVar[list[str]] = [
        "Technology",
        "Healthcare",
        "Finance",
        "Energy",
        "Consumer",
        "Industrials",
        "Materials",
        "Utilities",
        "Real Estate",
    ]
    COUNTRIES: ClassVar[list[str]] = [
        "USA",
        "UK",
        "Germany",
        "Canada",
        "Singapore",
        "France",
        "Japan",
        "China",
        "India",
        "Australia",
    ]

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v:
            raise ValueError("Ticker is required")
        if not re.match("^[A-Z0-9 ]{2,10}$", v):
            raise ValueError("Ticker must be 2-10 uppercase alphanumeric characters")
        return v

    @field_validator("structure")
    @classmethod
    def validate_structure(cls, v: str) -> str:
        if not v:
            raise ValueError("Structure is required")
        if v not in cls.STRUCTURES:
            raise ValueError(f"Structure must be one of: {', '.join(cls.STRUCTURES)}")
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in cls.COUNTRIES:
            raise ValueError("Invalid country selection")
        return v

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in cls.SECTORS:
            raise ValueError("Invalid sector selection")
        return v

    @field_validator(
        "shares_amount",
        "offering_price",
        "market_cap",
        "price_on_pricing_date",
        "vol_on_pricing_date",
        "offer_price_usd",
        "gross_spread",
        "net_purchase_price",
        "primary_shares",
        "secondary_shares",
    )
    @classmethod
    def validate_positive_numbers(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Value must be positive")
        return v

    @field_validator("fee_percent", "inst_own_pct")
    @classmethod
    def validate_percentages(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (not 0 <= v <= 100):
            raise ValueError("Percentage must be between 0-100")
        return v

    @field_validator("pricing_date", "announce_date", "warrants_exp", "pmi_date")
    @classmethod
    def validate_dates(cls, v: Optional[str]) -> Optional[str]:
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError as e:
                logging.exception(f"Error: {e}")
                raise ValueError("Invalid date format (YYYY-MM-DD)")
        return v

    @model_validator(mode="after")
    def validate_cross_fields(self) -> "Deal":
        if self.flag_bought and (not self.offering_price):
            raise ValueError("Offering price is required for Bought Deals")
        if self.warrants_min and self.warrants_min > 0:
            if not self.warrants_strike:
                raise ValueError("Warrants Strike required when warrants exist")
            if not self.warrants_exp:
                raise ValueError("Warrants Exp required when warrants exist")
        if self.pricing_date and self.announce_date:
            p_date = datetime.strptime(self.pricing_date, "%Y-%m-%d")
            a_date = datetime.strptime(self.announce_date, "%Y-%m-%d")
            if p_date < a_date:
                raise ValueError("Pricing date cannot be before announce date")
        total = self.shares_amount or 0
        prim = self.primary_shares or 0
        sec = self.secondary_shares or 0
        if total > 0 and prim > 0 and (sec > 0):
            if abs(total - (prim + sec)) > total * 0.01:
                pass
        return self


class Alert(TypedDict):
    id: int
    severity: str
    title: str
    message: str
    timestamp: str
    deal_ticker: Optional[str]
    is_dismissed: bool