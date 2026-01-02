import reflex as rx
from typing import Optional
from faker import Faker
import random
from datetime import datetime
from app.states.schema import Deal, DealStatus
from app.states.deal_form_state import DealFormState

fake = Faker()


class DealState(rx.State):
    deals: list[Deal] = []
    filtered_deals: list[Deal] = []
    search_query: str = ""
    active_review_deal: Optional[Deal] = None
    form_data: dict = {}
    current_page: int = 1
    items_per_page: int = 10
    selected_deal_ids: list[str] = []

    @rx.var
    def pending_deals(self) -> list[Deal]:
        return [d for d in self.deals if d.status == DealStatus.PENDING_REVIEW]

    @rx.var
    def active_deals_count(self) -> int:
        return len([d for d in self.deals if d.status == DealStatus.ACTIVE])

    @rx.var
    def total_pages(self) -> int:
        return -(-len(self.filtered_deals) // self.items_per_page)

    @rx.var
    def paginated_deals(self) -> list[Deal]:
        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        return self.filtered_deals[start:end]

    @rx.var
    def all_selected(self) -> bool:
        if not self.paginated_deals:
            return False
        return all(
            (deal.ticker in self.selected_deal_ids for deal in self.paginated_deals)
        )

    @rx.event
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1

    @rx.event
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1

    @rx.event
    def toggle_select_all(self):
        current_page_ids = [d.ticker for d in self.paginated_deals]
        if self.all_selected:
            self.selected_deal_ids = [
                pid for pid in self.selected_deal_ids if pid not in current_page_ids
            ]
        else:
            for pid in current_page_ids:
                if pid not in self.selected_deal_ids:
                    self.selected_deal_ids.append(pid)

    @rx.event
    def toggle_select_deal(self, deal_ticker: str):
        if deal_ticker in self.selected_deal_ids:
            self.selected_deal_ids.remove(deal_ticker)
        else:
            self.selected_deal_ids.append(deal_ticker)

    @rx.event
    def delete_selected_deals(self):
        self.deals = [d for d in self.deals if d.ticker not in self.selected_deal_ids]
        self.selected_deal_ids = []
        self.filter_deals()
        yield rx.toast("Selected deals deleted.", position="bottom-right")

    @rx.event
    def load_data(self):
        if not self.deals:
            self._generate_fake_data()
        self.filter_deals()

    def _generate_fake_data(self):
        structures = ["IPO", "M&A", "Spin-off", "Follow-on", "Convertible"]
        sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer"]
        countries = ["USA", "UK", "Germany", "Canada", "Singapore"]
        statuses = list(DealStatus)
        new_deals = []
        for _ in range(50):
            status = random.choice(statuses)
            ticker = fake.unique.lexify(text="????").upper()
            deal = Deal(
                ticker=ticker,
                structure=random.choice(structures),
                company_name=fake.company(),
                pricing_date=fake.date_this_year().isoformat(),
                announce_date=fake.date_this_year().isoformat(),
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
                source_file=f"{ticker}_term_sheet.pdf",
                deal_description=fake.paragraph(nb_sentences=3),
                reg_id=f"333-{random.randint(100000, 999999)}",
                warrants_min=random.randint(0, 5),
                warrants_strike=round(random.uniform(10.0, 100.0), 2),
            )
            new_deals.append(deal)
        self.deals = sorted(new_deals, key=lambda x: x.created_at, reverse=True)

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.current_page = 1
        self.filter_deals()

    @rx.event
    def filter_deals(self):
        if not self.search_query:
            self.filtered_deals = self.deals
        else:
            query = self.search_query.lower()
            self.filtered_deals = [
                d
                for d in self.deals
                if query in d.ticker.lower() or query in (d.company_name or "").lower()
            ]

    @rx.event
    async def select_deal_for_review(self, deal_ticker: str):
        deal = next((d for d in self.deals if d.ticker == deal_ticker), None)
        if deal:
            self.active_review_deal = deal
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal.dict(), "review")

    upload_tab: str = "upload"

    @rx.event
    def set_upload_tab(self, tab: str):
        self.upload_tab = tab

    @rx.event
    def handle_form_change(self, field: str, value: str):
        self.form_data[field] = value

    @rx.event
    def clear_form(self):
        self.form_data = {}
        self.active_review_deal = None

    @rx.event
    def save_draft(self, form_data: dict):
        self._save_deal(form_data, DealStatus.DRAFT)
        yield rx.toast("Deal saved as draft.", position="bottom-right", duration=3000)

    @rx.event
    async def approve_current_deal(self):
        if self.active_review_deal:
            deal_ticker = self.active_review_deal.ticker
            form_state = await self.get_state(DealFormState)
            updated_values = form_state.form_values
            deal_idx = next(
                (i for i, d in enumerate(self.deals) if d.ticker == deal_ticker), -1
            )
            if deal_idx >= 0:
                deal = self.deals[deal_idx]
                for key, value in updated_values.items():
                    if hasattr(deal, key):
                        setattr(deal, key, value)
                deal.status = DealStatus.ACTIVE
                deal.updated_at = datetime.now()
                self.deals = list(self.deals)
            self.active_review_deal = None
            form_state.reset_form()
            self.filter_deals()
            yield rx.toast(
                "Deal approved and activated.", position="bottom-right", duration=3000
            )

    @rx.event
    def reject_current_deal(self):
        if self.active_review_deal:
            deal_ticker = self.active_review_deal.ticker
            self.deals = [d for d in self.deals if d.ticker != deal_ticker]
            self.active_review_deal = None
            self.form_data = {}
            self.filter_deals()
            yield rx.toast(
                "Deal rejected and removed.", position="bottom-right", duration=3000
            )

    def _save_deal(self, form_data: dict, status: DealStatus):
        bool_fields = ["flag_bought", "flag_clean_up", "flag_top_up"]
        for field in bool_fields:
            form_data[field] = form_data.get(field) == "on"
        float_fields = [
            "shares_amount",
            "offering_price",
            "market_cap",
            "avg_volume",
            "warrants_strike",
        ]
        for field in float_fields:
            if form_data.get(field) == "":
                form_data[field] = None
        ticker = form_data.get("ticker", "UNKNOWN")
        existing_idx = next(
            (i for i, d in enumerate(self.deals) if d.ticker == ticker), -1
        )
        if existing_idx >= 0:
            for key, value in form_data.items():
                if hasattr(self.deals[existing_idx], key):
                    setattr(self.deals[existing_idx], key, value)
            self.deals[existing_idx].status = status
            self.deals[existing_idx].updated_at = datetime.now()
        else:
            if not form_data.get("ticker"):
                form_data["ticker"] = fake.unique.lexify(text="????").upper()
            deal = Deal(**form_data)
            deal.status = status
            deal.ai_confidence_score = (
                100 if status == DealStatus.DRAFT else random.randint(80, 100)
            )
            self.deals.insert(0, deal)
        self.deals = list(self.deals)
        self.filter_deals()

    @rx.event
    async def submit_new_deal(self, form_data: dict):
        form_state = await self.get_state(DealFormState)
        merged_data = {**form_state.form_values, **form_data}
        self._save_deal(merged_data, DealStatus.PENDING_REVIEW)
        yield rx.toast(
            "Deal submitted for review.", position="bottom-right", duration=3000
        )