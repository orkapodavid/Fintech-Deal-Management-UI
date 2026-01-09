import reflex as rx
from typing import Optional
from datetime import datetime
from app.states.schema import Deal, DealStatus
from app.states.deal_form_state import DealFormState
from app.services.deal_service import DealService

deal_service = DealService()


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
        return all((deal.id in self.selected_deal_ids for deal in self.paginated_deals))

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
        current_page_ids = [d.id for d in self.paginated_deals]
        if self.all_selected:
            self.selected_deal_ids = [
                pid for pid in self.selected_deal_ids if pid not in current_page_ids
            ]
        else:
            for pid in current_page_ids:
                if pid not in self.selected_deal_ids:
                    self.selected_deal_ids.append(pid)

    @rx.event
    def toggle_select_deal(self, deal_id: str):
        if deal_id in self.selected_deal_ids:
            self.selected_deal_ids.remove(deal_id)
        else:
            self.selected_deal_ids.append(deal_id)

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
        # Call service to delete deals
        for deal_id in self.selected_deal_ids:
            deal_service.delete_deal(deal_id)

        # Refresh local state
        self.deals = deal_service.get_deals()
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
            deals_to_export = [d for d in self.deals if d.id in self.selected_deal_ids]
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
        deal_id = self.selected_deal_ids[0]
        deal = next((d for d in self.deals if d.id == deal_id), None)
        if deal:
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, mode="edit")
            return rx.redirect(f"/add?mode=edit&id={deal_id}")

    @rx.event
    def load_data(self):
        self.deals = deal_service.get_deals()

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
    async def select_deal_for_review(self, deal_id: str):
        deal = next((d for d in self.deals if d.id == deal_id), None)
        if deal:
            self.active_review_deal = deal
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, "review")
            yield rx.toast(f"Viewing deal: {deal.ticker}", position="bottom-right")

    @rx.event
    async def on_review_page_load(self):
        """Handle review page load - check query params to load deal from URL."""
        deal_id = self.router.page.params.get("id")
        if deal_id:
            deal = next((d for d in self.deals if d.id == deal_id), None)
            if deal:
                self.active_review_deal = deal
                form_state = await self.get_state(DealFormState)
                form_state.load_deal_for_edit(deal, "review")
        else:
            # No id in URL, clear active review
            self.active_review_deal = None

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
            deal_id = self.active_review_deal.id
            form_state = await self.get_state(DealFormState)
            updated_values = form_state.form_values

            # Find and update deal
            deal = deal_service.get_deal_by_id(deal_id)
            if deal:
                for k, v in updated_values.items():
                    if v == "":
                        v = None
                    if hasattr(deal, k):
                        setattr(deal, k, v)
                deal.status = DealStatus.ACTIVE
                deal.updated_at = datetime.now().isoformat()
                deal_service.save_deal(deal)

                # Refresh local state
                self.deals = deal_service.get_deals()

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
            deal_id = self.active_review_deal.id
            deal_service.delete_deal(deal_id)
            self.deals = deal_service.get_deals()
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
            # We don't have access to fake here anymore, but user should provide ticker or we generate a placeholder
            # ideally the form validation handles this.
            # providing a fallback just in case
            import random
            import string

            ticker = "".join(random.choices(string.ascii_uppercase, k=4))
            processed_data["ticker"] = ticker

        now = datetime.now().isoformat()

        # Check if we're editing by id first, then fallback to ticker
        deal_id = processed_data.get("id")
        current_deal = None

        if deal_id:
            current_deal = deal_service.get_deal_by_id(deal_id)

        if current_deal is None:
            current_deal = deal_service.get_deal_by_ticker(ticker)

        if current_deal:
            for k, v in processed_data.items():
                if hasattr(current_deal, k):
                    setattr(current_deal, k, v)
            current_deal.status = status
            current_deal.updated_at = now
            deal_service.save_deal(current_deal)
        else:
            processed_data["status"] = status
            processed_data["created_at"] = now
            processed_data["updated_at"] = now
            if "ai_confidence_score" not in processed_data:
                processed_data["ai_confidence_score"] = (
                    100
                    if status == DealStatus.DRAFT
                    else 85  # Default high confidence for manually entered deals
                )
            new_deal = Deal(**processed_data)
            deal_service.save_deal(new_deal)

        # Refresh local list
        self.deals = deal_service.get_deals()

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
