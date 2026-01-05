import reflex as rx


def confirmation_dialog(
    is_open: rx.Var[bool],
    title: str,
    message: str,
    on_confirm: rx.event.EventHandler,
    on_cancel: rx.event.EventHandler,
) -> rx.Component:
    return rx.cond(
        is_open,
        rx.el.div(
            rx.el.div(
                class_name="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "triangle-alert", class_name="h-6 w-6 text-red-600"
                                ),
                                class_name="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10",
                            ),
                            rx.el.div(
                                rx.el.h3(
                                    title,
                                    class_name="text-base font-semibold leading-6 text-gray-900",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        message, class_name="text-sm text-gray-500"
                                    ),
                                    class_name="mt-2",
                                ),
                                class_name="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left",
                            ),
                            class_name="sm:flex sm:items-start",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Delete",
                                on_click=on_confirm,
                                class_name="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto",
                            ),
                            rx.el.button(
                                "Cancel",
                                on_click=on_cancel,
                                class_name="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto",
                            ),
                            class_name="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse",
                        ),
                        class_name="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6",
                    ),
                    class_name="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0",
                ),
                class_name="fixed inset-0 z-50 overflow-y-auto",
            ),
            class_name="relative z-50",
        ),
    )