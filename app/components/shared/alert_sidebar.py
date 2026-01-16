import reflex as rx
from app.states.alerts.alert_state import AlertState
from app.states.shared.schema import Alert


def format_timestamp_display(timestamp: rx.Var) -> rx.Var:
    """Extract and format time from ISO timestamp for display.

    Takes ISO string like '2026-01-14T23:10:25.123456' and returns 'HH:MM'
    ISO format positions: 0123456789...  ->  2026-01-14T23:10:25
    Position 11 is 'T', so time starts at position 12.
    """
    # Extract time portion: HH:MM (positions 11-16, but 11 is 'T', so use 11:17 to get T23:10 then slice off T)
    # Actually: position 11='T', 12-13='23', 14=':', 15-16='10'
    # So for HH:MM we want [11:16] but that gives 'T23:1', we need [11:17] for 'T23:10' minus T
    # Simplest: take positions 11:16 which is 5 chars starting at T -> use slice adjustment
    return timestamp.to_string().split("T")[1][:5]


def alert_item(alert: Alert) -> rx.Component:
    border_color = rx.match(
        alert.severity,
        ("critical", "border-l-4 border-l-red-500"),
        ("warning", "border-l-4 border-l-orange-400"),
        ("system", "border-l-4 border-l-blue-500"),
        "border-l-4 border-l-gray-300",
    )
    badge_color = rx.match(
        alert.severity,
        ("critical", "text-red-700 bg-red-50"),
        ("warning", "text-orange-700 bg-orange-50"),
        ("system", "text-blue-700 bg-blue-50"),
        "text-gray-700 bg-gray-50",
    )
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    alert.severity.upper(),
                    class_name=f"text-[10px] font-bold px-1.5 py-0.5 rounded {badge_color}",
                ),
                rx.el.span(
                    format_timestamp_display(alert.timestamp),
                    class_name="text-xs text-gray-400",
                ),
                rx.el.button(
                    rx.icon("x", size=14),
                    on_click=lambda: AlertState.dismiss_alert(alert.id),
                    class_name="text-gray-400 hover:text-gray-600",
                ),
                class_name="flex items-center justify-between mb-1",
            ),
            rx.el.h4(
                alert.title,
                class_name="text-sm font-semibold text-gray-900 mb-1 leading-tight",
            ),
            rx.el.p(alert.message, class_name="text-xs text-gray-600 line-clamp-2"),
            rx.el.div(
                rx.el.button(
                    "Fix",
                    class_name="text-[10px] font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded hover:bg-blue-100 mr-2",
                ),
                rx.el.button(
                    "Ignore",
                    on_click=lambda: AlertState.dismiss_alert(alert.id),
                    class_name="text-[10px] font-medium text-gray-500 hover:text-gray-700",
                ),
                class_name="mt-2 flex items-center",
            ),
            class_name="p-3",
        ),
        class_name=f"bg-white border border-gray-100 shadow-sm rounded-lg mb-3 hover:shadow-md transition-shadow {border_color}",
    )


def alert_sidebar() -> rx.Component:
    return rx.cond(
        AlertState.show_sidebar,
        rx.el.aside(
            rx.el.div(
                rx.icon("triangle_alert", class_name="text-orange-500 w-5 h-5 mr-2"),
                rx.el.h3("Validation Alerts", class_name="font-semibold text-gray-800"),
                rx.el.div(class_name="flex-1"),
                rx.el.button(
                    rx.icon("panel-right-close", size=18),
                    on_click=AlertState.toggle_sidebar,
                    class_name="text-gray-400 hover:text-gray-600",
                ),
                class_name="flex items-center p-4 border-b border-gray-100",
            ),
            rx.el.div(
                rx.foreach(AlertState.alerts, alert_item),
                class_name="p-4 overflow-y-auto h-[calc(100vh-140px)]",
            ),
            rx.el.div(
                rx.el.button(
                    "View All Alerts",
                    class_name="w-full py-2 text-xs font-medium text-gray-600 border border-gray-200 rounded hover:bg-gray-50 bg-white",
                ),
                class_name="p-4 border-t border-gray-100 bg-gray-50",
            ),
            class_name="w-80 bg-gray-50 border-l border-gray-200 flex-shrink-0 flex flex-col h-[calc(100vh-64px)] transition-all duration-300",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("bell", size=20),
                on_click=AlertState.toggle_sidebar,
                class_name="p-3 text-gray-500 hover:bg-gray-100 rounded-lg m-2",
            ),
            class_name="w-16 border-l border-gray-200 bg-white flex flex-col items-center h-[calc(100vh-64px)]",
        ),
    )
