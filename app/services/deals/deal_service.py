from typing import List, Optional
from datetime import datetime
import random
from faker import Faker
from app.states.shared.schema import Deal, DealStatus

fake = Faker()


class DealService:
    def __init__(self):
        self._deals: List[Deal] = []
        self._initialized = False

    def get_deals(self) -> List[Deal]:
        if not self._initialized:
            self._generate_fake_data()
            self._initialized = True
        return self._deals

    def get_deal_by_id(self, deal_id: str) -> Optional[Deal]:
        return next((d for d in self._deals if d.id == deal_id), None)

    def get_deal_by_ticker(self, ticker: str) -> Optional[Deal]:
        return next((d for d in self._deals if d.ticker == ticker), None)

    def save_deal(self, deal: Deal) -> Deal:
        # Check if update or create
        existing_index = next(
            (i for i, d in enumerate(self._deals) if d.id == deal.id), None
        )

        if existing_index is not None:
            self._deals[existing_index] = deal
        else:
            self._deals.append(deal)
        return deal

    def delete_deal(self, deal_id: str) -> bool:
        initial_len = len(self._deals)
        self._deals = [d for d in self._deals if d.id != deal_id]
        return len(self._deals) < initial_len

    def _generate_fake_data(self):
        structures = ["IPO", "M&A", "Spin-off", "Follow-on", "Convertible"]
        sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer"]
        countries = ["USA", "UK", "Germany", "Canada", "Singapore"]
        statuses = [s.value for s in DealStatus]

        for _ in range(50):
            status = random.choice(statuses)
            ticker = fake.unique.lexify(text="????").upper()
            now = datetime.now().isoformat()
            warrants_min = random.randint(0, 5)
            if warrants_min > 0:
                warrants_strike = round(random.uniform(10.0, 100.0), 2)
                warrants_exp = fake.date_this_year().isoformat()
            else:
                warrants_strike = None
                warrants_exp = None

            announce_dt = fake.date_this_year()
            pricing_dt = fake.date_between(start_date=announce_dt, end_date="+30d")

            deal = Deal(
                ticker=ticker,
                structure=random.choice(structures),
                company_name=fake.company(),
                pricing_date=pricing_dt.isoformat(),
                announce_date=announce_dt.isoformat(),
                pmi_date=fake.date_this_year().isoformat(),
                shares_amount=round(random.uniform(1.0, 50.0), 2),
                offering_price=round(random.uniform(10.0, 500.0), 2),
                market_cap=round(random.uniform(100.0, 10000.0), 2),
                avg_volume=round(random.uniform(100000, 5000000), 2),
                gross_spread=round(random.uniform(1.0, 7.0), 2),
                net_purchase_price=round(random.uniform(90.0, 480.0), 2),
                status=status,
                ai_confidence_score=random.randint(30, 99),
                flag_bought=random.choice([True, False]),
                flag_clean_up=random.choice([True, False]),
                flag_top_up=random.choice([True, False]),
                sector=random.choice(sectors),
                country=random.choice(countries),
                source_file=f"\\\\fileserver\\deals\\2026\\{ticker}_term_sheet.pdf",
                deal_description=fake.paragraph(nb_sentences=3),
                reg_id=f"333-{random.randint(100000, 999999)}",
                warrants_min=warrants_min,
                warrants_strike=warrants_strike,
                warrants_exp=warrants_exp,
                created_at=now,
                updated_at=now,
                concurrent=None,
                id_bb_global=None,
                id_sedol1=None,
                action_id=None,
                first_trade_date=None,
                inst_own_date=None,
                price_on_pricing_date=None,
                vol_on_pricing_date=None,
                offer_price_usd=None,
                fx_rate=None,
                fee_percent=None,
                reported_shares=None,
                bbg_shares=None,
                primary_shares=None,
                secondary_shares=None,
                eqy_sh_out=None,
                eqy_float=None,
                inst_own_pct=None,
                bics_level=None,
                avg_daily_val=None,
                vix=None,
                vol_90_day=None,
                short_int=None,
                cdr_exch_code=None,
            )
            self._deals.append(deal)
