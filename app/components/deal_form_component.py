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


def deal_form_component() -> rx.Component:
    """Reusable Deal Form Component for Add and Review pages."""
    is_review = DealFormState.form_mode == "review"
    return rx.el.form(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("building-2", class_name="w-4 h-4 text-gray-400 mr-2"),
                    rx.el.h3(
                        "Identity", class_name="text-sm font-semibold text-gray-900"
                    ),
                    class_name="flex items-center mb-4 pb-2 border-b border-gray-100",
                ),
                rx.el.div(
                    form_field("Ticker", "ticker", placeholder="e.g. AAPL"),
                    form_field("Structure", "structure", placeholder="e.g. IPO"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Concurrent", "concurrent"),
                    form_field("Action ID", "action_id", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("ID BB Global", "id_bb_global"),
                    form_field("ID SEDOL1", "id_sedol1"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                form_field("Company Name", "company_name"),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("dollar-sign", class_name="w-4 h-4 text-gray-400 mr-2"),
                    rx.el.h3(
                        "Financials", class_name="text-sm font-semibold text-gray-900"
                    ),
                    class_name="flex items-center mb-4 pb-2 border-b border-gray-100",
                ),
                rx.el.div(
                    form_field("Pricing Date", "pricing_date", type_="date"),
                    form_field("Announce Date", "announce_date", type_="date"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Shares Amount (M)", "shares_amount", type_="number"),
                    form_field("Offering Price ($)", "offering_price", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Market Cap (M)", "market_cap", type_="number"),
                    form_field("Offer Price USD", "offer_price_usd", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Gross Spread", "gross_spread", type_="number"),
                    form_field(
                        "Net Purchase Price", "net_purchase_price", type_="number"
                    ),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("PMI Date", "pmi_date", type_="date"),
                    form_field("Fee Percent", "fee_percent", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("pie-chart", class_name="w-4 h-4 text-gray-400 mr-2"),
                    rx.el.h3(
                        "Structure & Warrants",
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    class_name="flex items-center mb-4 pb-2 border-b border-gray-100",
                ),
                rx.el.div(
                    form_field("Primary Shares", "primary_shares", type_="number"),
                    form_field("Secondary Shares", "secondary_shares", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Warrants Min", "warrants_min", type_="number"),
                    form_field("Warrants Strike", "warrants_strike", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Warrants Exp", "warrants_exp", type_="date"),
                    class_name="grid grid-cols-1 gap-4",
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("scale", class_name="w-4 h-4 text-gray-400 mr-2"),
                    rx.el.h3(
                        "Regulatory & Risk",
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    class_name="flex items-center mb-4 pb-2 border-b border-gray-100",
                ),
                rx.el.div(
                    form_field("Reg ID", "reg_id"),
                    form_field("CDR Exch Code", "cdr_exch_code"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("Avg Volume", "avg_volume", type_="number"),
                    form_field("Short Interest", "short_int", type_="number"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    form_field("VIX", "vix", type_="number"),
                    form_field("Vol 90 Day", "vol_90_day"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("tag", class_name="w-4 h-4 text-gray-400 mr-2"),
                    rx.el.h3(
                        "Classification",
                        class_name="text-sm font-semibold text-gray-900",
                    ),
                    class_name="flex items-center mb-4 pb-2 border-b border-gray-100",
                ),
                rx.el.div(
                    form_field("Country", "country"),
                    form_field("Sector", "sector"),
                    class_name="grid grid-cols-2 gap-4",
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            name="flag_bought",
                            default_checked=DealFormState.form_values["flag_bought"].to(
                                bool
                            ),
                            class_name="rounded text-blue-600 focus:ring-blue-500 mr-2",
                        ),
                        "Bought Deal",
                        class_name="text-sm text-gray-600",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            name="flag_clean_up",
                            default_checked=DealFormState.form_values[
                                "flag_clean_up"
                            ].to(bool),
                            class_name="rounded text-blue-600 focus:ring-blue-500 mr-2",
                        ),
                        "Clean Up",
                        class_name="text-sm text-gray-600",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            name="flag_top_up",
                            default_checked=DealFormState.form_values["flag_top_up"].to(
                                bool
                            ),
                            class_name="rounded text-blue-600 focus:ring-blue-500 mr-2",
                        ),
                        "Top Up",
                        class_name="text-sm text-gray-600",
                    ),
                    class_name="flex gap-6 mt-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Deal Description",
                        class_name="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 mt-6",
                    ),
                    rx.el.textarea(
                        name="deal_description",
                        default_value=DealFormState.form_values["deal_description"].to(
                            str
                        ),
                        on_change=lambda v: DealFormState.set_field_value(
                            "deal_description", v
                        ),
                        class_name="w-full h-24 rounded-md border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset border-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-blue-500 sm:text-sm sm:leading-6",
                    ),
                ),
                class_name="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-6",
            ),
            rx.cond(
                is_review,
                rx.el.div(
                    rx.el.div(
                        rx.el.button(
                            rx.icon("trash-2", class_name="w-4 h-4 mr-2"),
                            "Reject",
                            type="button",
                            on_click=DealState.reject_current_deal,
                            class_name="flex items-center justify-center px-4 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 font-medium transition-colors",
                        ),
                        class_name="flex gap-3",
                    ),
                    rx.el.button(
                        rx.icon("check", class_name="w-4 h-4 mr-2"),
                        "Approve & Activate",
                        type="button",
                        disabled=DealFormState.has_errors,
                        on_click=DealState.approve_current_deal,
                        class_name="flex items-center justify-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium shadow-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    class_name="flex items-center justify-between pt-4 border-t border-gray-200 sticky bottom-0 bg-white p-4 -mx-4 -mb-4 shadow-lg",
                ),
                rx.el.div(
                    rx.el.button(
                        "Clear Form",
                        type="button",
                        on_click=DealFormState.reset_form,
                        class_name="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors mr-3",
                    ),
                    rx.el.button(
                        "Save as Draft",
                        type="button",
                        on_click=lambda: DealState.save_draft(
                            DealFormState.form_values
                        ),
                        class_name="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors mr-3",
                    ),
                    rx.el.button(
                        "Submit to Pipeline",
                        type="submit",
                        disabled=~DealFormState.can_submit,
                        class_name="flex-1 justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed",
                    ),
                    class_name="flex items-center justify-end pt-4 border-t border-gray-200",
                ),
            ),
        ),
        on_submit=DealState.submit_new_deal,
        reset_on_submit=True,
    )