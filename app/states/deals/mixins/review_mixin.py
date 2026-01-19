import reflex as rx
from typing import Optional
from datetime import datetime
from app.states.shared.schema import Deal, DealStatus
from app.states.deals.deal_form_state import DealFormState
from app.services.deals.deal_service import DealService

deal_service = DealService()


class DealReviewMixin(rx.State, mixin=True):
    """Mixin for Review Deal logic."""

    active_review_deal: Optional[Deal] = None

    # PDF Viewer state
    n_pages: int = 1
    current_pdf_page: int = 1
    pdf_scale: float = 1.25  # Default readable zoom
    pdf_fit_width: bool = False  # Start with manual scale mode for reliable behavior
    pdf_container_width: int = 600  # Approximate width for 1/3 column

    @rx.var
    def pdf_effective_scale(self) -> float:
        """Compute effective scale. When fit-width, calculate from container."""
        if self.pdf_fit_width:
            # Approximate: assume typical A4 page width ~600px at scale 1.0
            # Container width / page width gives us the scale
            return max(0.5, min(2.0, self.pdf_container_width / 600))
        return self.pdf_scale

    @rx.var
    def document_path(self) -> str:
        """Return path to the deal's PDF document for the viewer.

        Returns the web-accessible path for the PDF viewer component.
        Falls back to sample file if source_file not set.
        """
        # DEMO MODE: For the prototype, we only have sample_deal.pdf in assets.
        # The mock deals have generated filenames that don't actually exist.
        # So we always return sample_deal.pdf for the viewer to ensure it renders.
        # In production, this would return the actual path:
        # if self.active_review_deal and self.active_review_deal.source_file:
        #     # ... logic to serve actual file ...
        return "/sample_deal.pdf"

    @rx.var
    def document_display_path(self) -> str:
        """Return the full file path to display in the UI."""
        if self.active_review_deal and self.active_review_deal.source_file:
            return self.active_review_deal.source_file
        return "/sample_deal.pdf (Demo)"

    @rx.var
    def document_network_path(self) -> str:
        """Return the network/local file path for direct access."""
        if self.active_review_deal and self.active_review_deal.source_file:
            return self.active_review_deal.source_file
        return ""

    @rx.var
    def has_network_path(self) -> bool:
        """Check if the document has a network path for local access."""
        if self.active_review_deal and self.active_review_deal.source_file:
            path = self.active_review_deal.source_file
            # Network paths start with \\ or //
            return path.startswith("\\\\") or path.startswith("//") or ":\\" in path
        return False

    def _get_file_url(self, path: str) -> str:
        """Convert a local/network path to a file:// URL."""
        if not path:
            return ""
        # Handle Windows network paths: \\server\share -> file://///server/share
        if path.startswith("\\\\"):
            return "file:///" + path.replace("\\", "/")
        # Handle Windows local paths: C:\path -> file:///C:/path
        if len(path) > 1 and path[1] == ":":
            return "file:///" + path.replace("\\", "/")
        # Unix paths
        return "file://" + path

    @rx.event
    def open_pdf_local(self):
        """Open the PDF file from the local/network path.

        Copies the path to clipboard and shows an alert with instructions.
        Browsers block file:// URLs from web pages for security.
        """
        if self.active_review_deal and self.active_review_deal.source_file:
            path = self.active_review_deal.source_file
            # Escape backslashes for JavaScript string
            js_path = path.replace("\\", "\\\\")

            return rx.call_script(f'''
                (function() {{
                    const path = "{js_path}";
                    
                    // Copy path to clipboard
                    navigator.clipboard.writeText(path).then(function() {{
                        alert('Path copied to clipboard!\\n\\nPaste this path in Windows Explorer to open the file:\\n\\n' + path);
                    }}).catch(function(err) {{
                        console.error('Could not copy path: ', err);
                        alert('File path:\\n\\n' + path + '\\n\\nPlease copy this path manually and paste in Windows Explorer.');
                    }});
                }})();
            ''')

    @rx.event
    def on_pdf_load_success(self, info: dict):
        """Handle PDF load success, update page count."""
        num_pages = info.get("numPages", 1)
        self.n_pages = int(num_pages) if num_pages else 1
        # Clamp current page to valid range
        if self.current_pdf_page > self.n_pages:
            self.current_pdf_page = self.n_pages
        if self.current_pdf_page < 1:
            self.current_pdf_page = 1

    @rx.event
    def on_pdf_load_error(self, error: dict):
        """Handle PDF load error."""
        pass  # Silently handle for now; can add toast notification if needed

    @rx.event
    def pdf_prev_page(self):
        """Navigate to previous PDF page."""
        self.current_pdf_page = max(1, self.current_pdf_page - 1)

    @rx.event
    def pdf_next_page(self):
        """Navigate to next PDF page."""
        self.current_pdf_page = min(self.n_pages, self.current_pdf_page + 1)

    @rx.event
    def pdf_zoom_in(self):
        """Zoom in (increases scale)."""
        self.pdf_fit_width = False
        self.pdf_scale = min(3.0, round(self.pdf_scale + 0.25, 2))

    @rx.event
    def pdf_zoom_out(self):
        """Zoom out (decreases scale)."""
        self.pdf_fit_width = False
        self.pdf_scale = max(0.5, round(self.pdf_scale - 0.25, 2))

    @rx.event
    def pdf_zoom_reset(self):
        """Reset zoom to default."""
        self.pdf_fit_width = False
        self.pdf_scale = 1.25

    @rx.event
    def pdf_toggle_fit_width(self):
        """Toggle fit-to-width mode."""
        self.pdf_fit_width = not self.pdf_fit_width

    @rx.event
    def set_pdf_container_width(self, width: int):
        """Update container width from client side."""
        self.pdf_container_width = width

    @rx.var
    def pending_deals(self) -> list[Deal]:
        # Requires self.deals from ListMixin or Main State
        if not hasattr(self, "deals"):
            return []
        return [d for d in self.deals if d.status == DealStatus.PENDING_REVIEW]

    @rx.var
    def active_deals_count(self) -> int:
        if not hasattr(self, "deals"):
            return 0
        return len([d for d in self.deals if d.status == DealStatus.ACTIVE])

    @rx.event
    async def select_deal_for_review(self, deal_id: str):
        deal = next((d for d in self.deals if d.id == deal_id), None)
        if deal:
            self.active_review_deal = deal
            form_state = await self.get_state(DealFormState)
            form_state.load_deal_for_edit(deal, "review")
            # In route-based app, we might also want to push route, but
            # if we are just clicking in list page to go to review, we should use rx.link
            # However this event loads the state.
            # If used from DealList, we might want to redirect.
            # But the plan says Review Page deals with query params.
            return rx.redirect(f"/deals/review?id={deal.id}")

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
            self.active_review_deal = None

    @rx.event
    async def approve_current_deal(self):
        if self.active_review_deal:
            deal_id = self.active_review_deal.id
            form_state = await self.get_state(DealFormState)
            updated_values = form_state.form_values

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
                if hasattr(self, "deals"):
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
            if hasattr(self, "deals"):
                self.deals = deal_service.get_deals()
            self.active_review_deal = None
            # self.form_data = {} # form_data is in AddMixin, maybe should be shared or just ignored here
            return [
                rx.toast(
                    "Deal rejected and removed.", position="bottom-right", duration=3000
                )
            ]
