import os

import reflex as rx

# SQLite writes create/remove journal files inside data/; without this Reflex
# restarts the backend on every reservation.
os.environ.setdefault("REFLEX_HOT_RELOAD_EXCLUDE_PATHS", "data")

config = rx.Config(
    app_name="reservas_ui",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ],
)
