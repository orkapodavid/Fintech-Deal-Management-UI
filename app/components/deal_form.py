import reflex as rx
from app.states.deal_state import DealState


def form_field(
    label: str,
    key: str,
    type_: str = "text",
    placeholder: str = "",
    confidence_score: int = 100,
    default_value: str | rx.Var = "",
) -> rx.Component:
    is_low_confidence = confidence_score < 60
    border_class = rx.cond(
        is_low_confidence,
        "border-amber-400 bg-amber-50 focus:ring-amber-200",
        "border-gray-200 bg-white focus:ring-blue-500",
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
                    "Verify", class_name="text-[10px] text-amber-600 font-bold ml-auto"
                ),
                None,
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.div(
            rx.el.input(
                type=type_,
                name=key,
                default_value=default_value,
                placeholder=placeholder,
                class_name=f"block w-full rounded-md border-0 py-2 text-gray-900 shadow-sm ring-1 ring-inset {border_class} placeholder:text-gray-400 focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6 pl-3",
            ),
            rx.cond(
                is_low_confidence,
                rx.icon(
                    "circle_alert",
                    class_name="absolute right-3 top-3 text-amber-500 w-4 h-4",
                ),
                None,
            ),
            class_name="relative mt-1",
        ),
        class_name="mb-4",
    )