import reflex as rx
from app.states.schema import Deal
from app.services.deal_service import DealService

deal_service = DealService()


class DealListMixin(rx.State, mixin=True):
    """Mixin for Deal List View (Filtering, Sorting, Pagination)."""

    deals: list[Deal] = []
    search_query: str = ""
    sort_column: str = "pricing_date"
    sort_direction: str = "desc"
    filter_status: str = "all"
    filter_start_date: str = ""
    filter_end_date: str = ""
    current_page: int = 1
    items_per_page: int = 10
    selected_deal_ids: list[str] = []
    show_delete_dialog: bool = False

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
        for deal_id in self.selected_deal_ids:
            deal_service.delete_deal(deal_id)

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
    def refresh_data(self):
        """Reloads data from the backend."""
        self.load_data()
        return rx.toast.info(
            "Data refreshed successfully.",
            position="bottom-right",
            duration=2000,
        )
