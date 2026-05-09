from textual.app import App
from textual.widgets import DataTable, Footer, Label


FAKE_DRIVERS = [
    {
        "position": 1,
        "driver_code": "HAM",
        "team": "Ferrari Scuderia",
        "tires": "soft",
        "gap": 0.00,
        "lap_time": "1.03.22",
    },
    {
        "position": 2,
        "driver_code": "LEC",
        "team": "Ferrari Scuderia",
        "tires": "soft",
        "gap": 0.72,
        "lap_time": "1.03.52",
    },
    {
        "position": 3,
        "driver_code": "VER",
        "team": "Red Bull Racing",
        "tires": "soft",
        "gap": 0.02,
        "lap_time": "1.03.55",
    },
    {
        "position": 4,
        "driver_code": "NOR",
        "team": "McClaren F1",
        "tires": "soft",
        "gap": 1.01,
        "lap_time": "1.04.02",
    },
]


class PitwallApp(App):
    CSS = """
    
    Screen {
        layout: vertical;
    }

    #title-bar {
        height: 3;
        background: black;
        content-align: center middle;
        text-style: bold;
        color: white;
    }

    #leaderboard {
        height: 1fr;
        border: solid green;
        margin: 0 1;
    }

    Footer {
        height: 2;
    }

    """

    def compose(self):
        yield Label("2026 Monza", id="title-bar")
        yield DataTable(id="leaderboard", cursor_type="none")
        yield Footer()

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("POS", "DRIVER", "TEAM", "TIRES", "GAP", "LAP TIME")
        for driver in FAKE_DRIVERS:
            table.add_row(
                driver["position"],
                driver["driver_code"],
                driver["team"],
                driver["tires"],
                driver["gap"],
                driver["lap_time"],
            )
