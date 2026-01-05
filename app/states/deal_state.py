import reflex as rx
from typing import Optional, Any
from faker import Faker
import random
from datetime import datetime
from app.states.schema import Deal, DealStatus
from app.states.deal_form_state import DealFormState
from app.states.alert_state import AlertState

fake = Faker()


class DealState(rx.State):
    deals: list[Deal] = []
    search_query: str = ""
    sort_column: str = "pricing_date"
    sort_direction: str = "desc"
    filter_status: str = "all"
    filter_start_date: str = ""
    filter_end_date: str = ""
    active_review_deal: Optional[Deal] = None
    form_data: dict = {}
    current_page: int = 1
    items_per_page: int = 10
    selected_deal_ids: list[str] = []

    @rx.var
    def filtered_deals(self) -> list[Deal]:
        deals = self.deals
        if self.search_query:
            q = self.search_query.lower()
            deals = [
                d
                for d in deals
                if d.ticker
                and q in d.ticker.lower()
                or (d.company_name and q in d.company_name.lower())
                or (d.sector and q in d.sector.lower())
                or (d.country and q in d.country.lower())
            ]
        if self.filter_status and self.filter_status != "all":
            deals = [d for d in deals if d.status == self.filter_status]
        if self.filter_start_date:
            deals = [
                d
                for d in deals
                if d.pricing_date and d.pricing_date >= self.filter_start_date
            ]
        if self.filter_end_date:
            deals = [
                d
                for d in deals
                if d.pricing_date and d.pricing_date <= self.filter_end_date
            ]
        if self.sort_column:

            @rx.event
            def sort_key(d):
                val = getattr(d, self.sort_column, None)
                if val is None:
                    if self.sort_column in [
                        "shares_amount",
                        "offering_price",
                        "market_cap",
                        "ai_confidence_score",
                    ]:
                        return -1.0
                    return ""
                return val

            reverse = self.sort_direction == "desc"
            deals = sorted(deals, key=sort_key, reverse=reverse)
        return deals

    @rx.var
    def pending_deals(self) -> list[Deal]:
        return [d for d in self.deals if d.status == DealStatus.PENDING_REVIEW]

    @rx.var
    def active_deals_count(self) -> int:
        return len([d for d in self.deals if d.status == DealStatus.ACTIVE])

    @rx.var
    def total_pages(self) -> int:
        if not self.filtered_deals:
            return 1
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

    show_delete_dialog: bool = False

    @rx.event
    def request_delete(self):
        if not self.selected_deal_ids:
            return rx.toast("No deals selected.", position="bottom-right")
        self.show_delete_dialog = True

    @rx.event
    def cancel_delete(self):
        self.show_delete_dialog = False

    @rx.event
    def confirm_delete(self):
        self.delete_selected_deals()
        self.show_delete_dialog = False

    @rx.event
    def delete_selected_deals(self):
        self.deals = [d for d in self.deals if d.ticker not in self.selected_deal_ids]
        self.selected_deal_ids = []
        return [rx.toast("Selected deals deleted.", position="bottom-right")]

    @rx.event
    def export_deals(self):
        import csv
        import io

        yield rx.toast(
            "Export started",
            description="Generating CSV and starting download...",
            position="bottom-right",
            duration=3000,
        )
        deals_to_export = []
        if self.selected_deal_ids:
            deals_to_export = [
                d for d in self.deals if d.ticker in self.selected_deal_ids
            ]
        else:
            deals_to_export = self.filtered_deals
        if not deals_to_export:
            return rx.toast("No deals to export.", position="bottom-right")
        output = io.StringIO()
        writer = csv.writer(output)
        headers = [
            "Ticker",
            "Structure",
            "Company",
            "Status",
            "Pricing Date",
            "Amount (M)",
            "Price",
            "Sector",
            "Country",
        ]
        writer.writerow(headers)
        for d in deals_to_export:
            writer.writerow(
                [
                    d.ticker,
                    d.structure,
                    d.company_name,
                    d.status.value,
                    d.pricing_date,
                    d.shares_amount,
                    d.offering_price,
                    d.sector,
                    d.country,
                ]
            )
        return rx.download(data=output.getvalue(), filename="deals_export.csv")

    @rx.event
    async def edit_selected_deal(self):
        if len(self.selected_deal_ids) != 1:
            return rx.toast("Select exactly one deal to edit.", position="bottom-right")
        ticker = self.selected_deal_ids[0]
        deal = next((d for d in self.deals if d.ticker == ticker), None)
        if deal:
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, mode="edit")
            return rx.redirect("/add")

    @rx.event
    def load_data(self):
        if not self.deals:
            self._generate_fake_data()

    def _generate_fake_data(self):
        structures = ["IPO", "M&A", "Spin-off", "Follow-on", "Convertible"]
        sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer"]
        countries = ["USA", "UK", "Germany", "Canada", "Singapore"]
        statuses = [s.value for s in DealStatus]
        new_deals = []
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
                source_file=f"{ticker}_term_sheet.pdf",
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
            new_deals.append(deal)
        self.deals = new_deals

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.current_page = 1

    @rx.event
    def sort_by_column(self, column: str):
        if self.sort_column == column:
            self.sort_direction = "desc" if self.sort_direction == "asc" else "asc"
        else:
            self.sort_column = column
            self.sort_direction = "asc"

    @rx.event
    def set_filter_status(self, status: str):
        self.filter_status = status
        self.current_page = 1

    @rx.event
    def set_filter_start_date(self, date: str):
        self.filter_start_date = date
        self.current_page = 1

    @rx.event
    def set_filter_end_date(self, date: str):
        self.filter_end_date = date
        self.current_page = 1

    @rx.event
    def clear_filters(self):
        self.search_query = ""
        self.filter_status = "all"
        self.filter_start_date = ""
        self.filter_end_date = ""
        self.sort_column = "pricing_date"
        self.sort_direction = "desc"
        self.current_page = 1

    @rx.event
    async def select_deal_for_review(self, deal_ticker: str):
        deal = next((d for d in self.deals if d.ticker == deal_ticker), None)
        if deal:
            self.active_review_deal = deal
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, "review")
            yield rx.toast(f"Viewing deal: {deal_ticker}", position="bottom-right")

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
        return rx.toast("Deal saved as draft.", position="bottom-right", duration=3000)

    @rx.event
    async def approve_current_deal(self):
        if self.active_review_deal:
            deal_ticker = self.active_review_deal.ticker
            form_state = await self.get_state(DealFormState)
            updated_values = form_state.form_values
            for i, d in enumerate(self.deals):
                if d.ticker == deal_ticker:
                    for k, v in updated_values.items():
                        if v == "":
                            v = None
                        if hasattr(d, k):
                            setattr(d, k, v)
                    d.status = DealStatus.ACTIVE
                    d.updated_at = datetime.now().isoformat()
                    self.deals[i] = d
                    break
            self.active_review_deal = None
            form_state.reset_form()
            return [
                rx.toast(
                    "Deal approved and activated.",
                    position="bottom-right",
                    duration=3000,
                )
            ]

    @rx.event
    def reject_current_deal(self):
        if self.active_review_deal:
            deal_ticker = self.active_review_deal.ticker
            self.deals = [d for d in self.deals if d.ticker != deal_ticker]
            self.active_review_deal = None
            self.form_data = {}
            return [
                rx.toast(
                    "Deal rejected and removed.", position="bottom-right", duration=3000
                )
            ]

    def _save_deal(self, form_data: dict, status: DealStatus):
        processed_data = form_data.copy()
        bool_fields = ["flag_bought", "flag_clean_up", "flag_top_up"]
        for field in bool_fields:
            val = processed_data.get(field)
            processed_data[field] = val == "on" or val is True
        float_fields = [
            "shares_amount",
            "offering_price",
            "market_cap",
            "avg_volume",
            "warrants_strike",
        ]
        for field in float_fields:
            if processed_data.get(field) == "":
                processed_data[field] = None
        ticker = processed_data.get("ticker")
        if not ticker:
            ticker = fake.unique.lexify(text="????").upper()
            processed_data["ticker"] = ticker
        now = datetime.now().isoformat()
        existing_deal_index = next(
            (i for i, d in enumerate(self.deals) if d.ticker == ticker), None
        )
        if existing_deal_index is not None:
            current_deal = self.deals[existing_deal_index]
            for k, v in processed_data.items():
                if hasattr(current_deal, k):
                    setattr(current_deal, k, v)
            current_deal.status = status
            current_deal.updated_at = now
            self.deals[existing_deal_index] = current_deal
        else:
            processed_data["status"] = status
            processed_data["created_at"] = now
            processed_data["updated_at"] = now
            if "ai_confidence_score" not in processed_data:
                processed_data["ai_confidence_score"] = (
                    100 if status == DealStatus.DRAFT else random.randint(80, 100)
                )
            new_deal = Deal(**processed_data)
            self.deals.append(new_deal)
        return rx.noop()

    @rx.event
    async def submit_new_deal(self, form_data: dict):
        form_state = await self.get_state(DealFormState)
        merged_data = {**form_state.form_values, **form_data}
        update = self._save_deal(merged_data, DealStatus.PENDING_REVIEW)
        return [
            update,
            rx.toast(
                "Deal submitted for review.", position="bottom-right", duration=3000
            ),
        ]

    @rx.event
    def refresh_data(self):
        """Reloads data from the backend."""
        self.load_data()
        return rx.toast(
            "Data refreshed successfully.",
            position="bottom-right",
            duration=2000,
            style={
                "background-color": "#EFF6FF",
                "color": "#1E40AF",
                "border": "1px solid #BFDBFE",
            },
        )

    @rx.event
    def show_settings(self):
        """Displays a settings toast placeholder."""
        return rx.toast(
            "Settings panel is under construction.",
            position="bottom-right",
            duration=3000,
            style={
                "background-color": "#F3F4F6",
                "color": "#374151",
                "border": "1px solid #E5E7EB",
            },
        )

    @rx.event
    def show_notifications(self):
        """Show notifications info."""
        return rx.toast(
            "You have new notifications.", position="bottom-right", duration=2000
        )

    @rx.event
    def logout(self):
        """Simulates user logout."""
        return rx.toast(
            "Logging out...",
            position="bottom-right",
            duration=2000,
            style={
                "background-color": "#FEF2F2",
                "color": "#991B1B",
                "border": "1px solid #FECACA",
            },
        )