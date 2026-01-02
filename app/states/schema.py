import reflex as rx
from sqlmodel import SQLModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class DealStatus(str, Enum):
    ACTIVE = "active"
    PENDING_REVIEW = "pending_review"
    DRAFT = "draft"


class Deal(SQLModel, table=True):
    ticker: str = Field(primary_key=True)
    structure: str = Field(default="")
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
    ai_confidence_score: int = 0
    source_file: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Alert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    message: str
    severity: str
    timestamp: datetime = Field(default_factory=datetime.now)
    deal_ticker: Optional[str] = Field(default=None, foreign_key="deal.ticker")
    is_dismissed: bool = False