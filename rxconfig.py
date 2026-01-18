import reflex as rx

config = rx.Config(
    app_name="app",
    plugins=[rx.plugins.TailwindV3Plugin()],
    frontend_packages=[
        "react-pdf@9.1.1",  # Required for PDF viewer component
    ],
)
