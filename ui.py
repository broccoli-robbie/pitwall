from textual.app import App, ComposeResult
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
        height: 2;
        background: black;
        content-align: center middle;
        text-style: bold;
        color: white;
    }

    #leaderboard {
        height: 1fr;
        border: solid red;
        margin: 0 1;
    }

    Footer {
        height: 1;
    }

    """

    def __init__(self, session):
        super().__init__()
        self.session = session
        self.current_lap = 1
        self.gap_mode = "interval"

    def compose(self) -> ComposeResult:
        yield Label(f"{self.session.year} {self.session.race_name}", id="title-bar")
        yield DataTable(id="leaderboard", cursor_type="none")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("POS", "DRIVER", "TEAM", "TIRES", "GAP", "LAP TIME")
        self._refresh_table()

    def _lap_label(self):
        return f"Lap {self.current_lap} / {self.total_laps}  < > to step"

    def _gap_mode_label(self):
        if self.gap_mode == "interval":
            return "Gap mode: Interval (gap to car ahead)  [T] to toggle"
        else:
            return "Gap mode: Leader gap (gap to P1)  [T] to toggle"


if __name__ == "__main__":
    app = PitwallApp()
    app.run()
