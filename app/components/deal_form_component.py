import reflex as rx
from app.states.deal_form_state import DealFormState
from app.states.deal_state import DealState


def form_field(
    label: str,
    key: str,
    type_: str = "text",
    placeholder: str = "",
    required: bool = False,
) -> rx.Component:
    """Reusable form field with validation and confidence highlighting."""
    error = DealFormState.field_errors[key]
    has_error = DealFormState.validation_results[key]["is_valid"] == False
    confidence_score = DealFormState.form_values["ai_confidence_score"].to(int)
    is_low_confidence = (DealFormState.form_mode == "review") & (confidence_score < 60)
    border_class = rx.cond(
        has_error,
        "border-red-300 focus:border-red-500 focus:ring-red-500 bg-red-50",
        rx.cond(
            is_low_confidence,
            "border-amber-400 bg-amber-50 focus:border-amber-500 focus:ring-amber-500",
            "border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white",
        ),
    )
    return rx.el.div(
        rx.el.div(
            rx.el.label(
                label,
                class_name="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1",
            ),
            rx.cond(
                is_low_confidence,
                rx.el.span(
                    "Low Confidence",
                    class_name="text-[10px] font-bold text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded",
                ),
                None,
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.input(
                type=type_,
                name=key,
                default_value=DealFormState.form_values[key].to(str),
                on_change=lambda v: DealFormState.set_field_value(key, v),
                on_blur=lambda: DealFormState.touch_field(key),
                placeholder=placeholder,
                class_name=f"block w-full rounded-md py-2 text-gray-900 shadow-sm ring-1 ring-inset {border_class} placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6 pl-3 transition-colors",
            ),
            rx.cond(
                has_error,
                rx.icon(
                    "circle-alert",
                    class_name="absolute right-3 top-2.5 text-red-500 w-5 h-5",
                ),
                rx.cond(
                    is_low_confidence,
                    rx.icon(
                        "triangle-alert",
                        class_name="absolute right-3 top-2.5 text-amber-500 w-5 h-5",
                    ),
                    None,
                ),
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
    """Compact form field for dense layouts."""
    error = DealFormState.field_errors[key]
    has_error = DealFormState.validation_results[key]["is_valid"] == False
    confidence_score = DealFormState.form_values["ai_confidence_score"].to(int)
    is_low_confidence = (DealFormState.form_mode == "review") & (confidence_score < 60)
    border_class = rx.cond(
        has_error,
        "border-red-300 focus:border-red-500 focus:ring-red-500 bg-red-50",
        rx.cond(
            is_low_confidence,
            "border-amber-400 bg-amber-50 focus:border-amber-500 focus:ring-amber-500",
            "border-gray-300 focus:border-blue-500 focus:ring-blue-500 bg-white",
        ),
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
                default_value=DealFormState.form_values[key].to(str),
                on_change=lambda v: DealFormState.set_field_value(key, v),
                on_blur=lambda: DealFormState.touch_field(key),
                placeholder=placeholder,
                class_name=f"block w-full rounded py-1.5 text-gray-900 shadow-sm ring-1 ring-inset {border_class} placeholder:text-gray-400 focus:ring-2 focus:ring-inset text-sm pl-2 transition-colors",
            ),
            rx.cond(
                has_error,
                rx.icon(
                    "circle-alert",
                    class_name="absolute right-2 top-1.5 text-red-500 w-4 h-4",
                ),
                rx.cond(
                    is_low_confidence,
                    rx.icon(
                        "triangle-alert",
                        class_name="absolute right-2 top-1.5 text-amber-500 w-4 h-4",
                    ),
                    None,
                ),
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
    """Compact section header for bento box cards."""
    return rx.el.div(
        rx.icon(icon, class_name="w-3.5 h-3.5 text-blue-500 mr-1.5"),
        rx.el.h3(
            title, class_name="text-xs font-semibold text-gray-900 uppercase tracking-wide"
        ),
        class_name="flex items-center mb-3 pb-1.5 border-b border-gray-100",
    )


def deal_form_component() -> rx.Component:
    """Reusable Deal Form Component with Bento Box layout for power users."""
    is_review = DealFormState.form_mode == "review"
    return rx.el.form(
        # 12-Column Bento Box Grid Layout
        rx.el.div(
            # === TOP ROW: Identity (7-col) + Classification (5-col) ===
            rx.el.div(
                # Identity Card - 7/12 columns on desktop
                rx.el.div(
                    section_header("building-2", "Identity"),
                    rx.el.div(
                        compact_form_field("Ticker", "ticker", placeholder="AAPL"),
                        compact_form_field("Structure", "structure", placeholder="IPO"),
                        compact_form_field("Concurrent", "concurrent"),
                        compact_form_field("Action ID", "action_id", type_="number"),
                        compact_form_field("ID BB Global", "id_bb_global"),
                        compact_form_field("ID SEDOL1", "id_sedol1"),
                        class_name="grid grid-cols-2 lg:grid-cols-3 gap-x-3 gap-y-1",
                    ),
                    compact_form_field("Company Name", "company_name"),
                    class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 h-full col-span-12 lg:col-span-7",
                ),
                # Classification Card - 5/12 columns on desktop
                rx.el.div(
                    section_header("tag", "Classification"),
                    rx.el.div(
                        compact_form_field("Country", "country"),
                        compact_form_field("Sector", "sector"),
                        class_name="grid grid-cols-2 gap-x-3 gap-y-1",
                    ),
                    rx.el.div(
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                name="flag_bought",
                                default_checked=DealFormState.form_values["flag_bought"].to(bool),
                                class_name="rounded text-blue-600 focus:ring-blue-500 mr-1.5 w-3.5 h-3.5",
                            ),
                            "Bought",
                            class_name="text-xs text-gray-600 flex items-center",
                        ),
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                name="flag_clean_up",
                                default_checked=DealFormState.form_values["flag_clean_up"].to(bool),
                                class_name="rounded text-blue-600 focus:ring-blue-500 mr-1.5 w-3.5 h-3.5",
                            ),
                            "Clean Up",
                            class_name="text-xs text-gray-600 flex items-center",
                        ),
                        rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                name="flag_top_up",
                                default_checked=DealFormState.form_values["flag_top_up"].to(bool),
                                class_name="rounded text-blue-600 focus:ring-blue-500 mr-1.5 w-3.5 h-3.5",
                            ),
                            "Top Up",
                            class_name="text-xs text-gray-600 flex items-center",
                        ),
                        class_name="flex gap-3 mt-2 pt-2 border-t border-gray-50",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Notes",
                            class_name="block text-[10px] font-bold text-gray-500 uppercase tracking-wider mb-1 mt-2",
                        ),
                        rx.el.textarea(
                            name="deal_description",
                            default_value=DealFormState.form_values["deal_description"].to(str),
                            on_change=lambda v: DealFormState.set_field_value("deal_description", v),
                            placeholder="Brief deal notes...",
                            class_name="w-full h-40 rounded border-gray-300 py-1 px-2 text-gray-900 shadow-sm ring-1 ring-inset focus:ring-2 focus:ring-inset focus:ring-blue-500 text-xs resize-none",
                        ),
                    ),
                    class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 h-full col-span-12 lg:col-span-5",
                ),
                class_name="grid grid-cols-12 gap-3 mb-3",
            ),
            # === MIDDLE ROW: Combined Financials + Structure (6-column dense grid) ===
            rx.el.div(
                section_header("dollar-sign", "Financials & Structure"),
                rx.el.div(
                    # Row 1: Dates + Primary/Secondary shares
                    compact_form_field("Pricing Date", "pricing_date", type_="date"),
                    compact_form_field("Announce Date", "announce_date", type_="date"),
                    compact_form_field("Primary Shares", "primary_shares", type_="number"),
                    compact_form_field("Secondary Shares", "secondary_shares", type_="number"),
                    compact_form_field("Shares (M)", "shares_amount", type_="number"),
                    compact_form_field("Offer Price ($)", "offering_price", type_="number"),
                    # Row 2: Financial metrics + Warrants
                    compact_form_field("Market Cap (M)", "market_cap", type_="number"),
                    compact_form_field("Offer USD", "offer_price_usd", type_="number"),
                    compact_form_field("Warrants Min", "warrants_min", type_="number"),
                    compact_form_field("Warrants Strike", "warrants_strike", type_="number"),
                    compact_form_field("Warrants Exp", "warrants_exp", type_="date"),
                    compact_form_field("Gross Spread", "gross_spread", type_="number"),
                    # Row 3: Remaining fields
                    compact_form_field("Net Purchase", "net_purchase_price", type_="number"),
                    compact_form_field("PMI Date", "pmi_date", type_="date"),
                    compact_form_field("Fee %", "fee_percent", type_="number"),
                    class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-3 gap-y-1",
                ),
                class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 mb-3",
            ),
            # === BOTTOM ROW: Regulatory & Risk (horizontal strip) ===
            rx.el.div(
                section_header("scale", "Regulatory & Risk"),
                rx.el.div(
                    compact_form_field("Reg ID", "reg_id"),
                    compact_form_field("CDR Exch Code", "cdr_exch_code"),
                    compact_form_field("Avg Volume", "avg_volume", type_="number"),
                    compact_form_field("Short Interest", "short_int", type_="number"),
                    compact_form_field("VIX", "vix", type_="number"),
                    compact_form_field("Vol 90 Day", "vol_90_day"),
                    class_name="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-x-3 gap-y-1",
                ),
                class_name="bg-white p-3 rounded-lg shadow-sm border border-gray-100 mb-3",
            ),
            # === ACTION BAR ===
            rx.cond(
                is_review,
                rx.el.div(
                    rx.el.div(
                        rx.el.button(
                            rx.icon("trash-2", class_name="w-4 h-4 mr-1.5"),
                            "Reject",
                            type="button",
                            on_click=DealState.reject_current_deal,
                            class_name="flex items-center justify-center px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 font-medium transition-colors text-sm",
                        ),
                        class_name="flex gap-3",
                    ),
                    rx.el.button(
                        rx.icon("check", class_name="w-4 h-4 mr-1.5"),
                        "Approve & Activate",
                        type="button",
                        disabled=DealFormState.has_errors,
                        on_click=DealState.approve_current_deal,
                        class_name="flex items-center justify-center px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm",
                    ),
                    class_name="flex items-center justify-between bg-white p-3 rounded-lg shadow-sm border border-gray-100",
                ),
                rx.el.div(
                    rx.el.button(
                        "Clear",
                        type="button",
                        on_click=DealFormState.reset_form,
                        class_name="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors text-sm mr-2",
                    ),
                    rx.el.button(
                        "Save Draft",
                        type="button",
                        on_click=lambda: DealState.save_draft(DealFormState.form_values),
                        class_name="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors text-sm mr-2",
                    ),
                    rx.el.button(
                        rx.cond(
                            DealFormState.form_mode == "edit",
                            "Update Deal",
                            "Submit to Pipeline",
                        ),
                        type="submit",
                        disabled=~DealFormState.can_submit,
                        class_name="px-4 py-1.5 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    class_name="flex items-center justify-end bg-white p-3 rounded-lg shadow-sm border border-gray-100",
                ),
            ),
        ),
        on_submit=DealState.submit_new_deal,
        reset_on_submit=True,
        key=DealFormState.form_key,
    )