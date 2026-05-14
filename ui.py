from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Label
from textual.binding import Binding
from data import LapSnapshot


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

    def _refresh_table(self):
        table = self.query_one(DataTable)
        table.clear()

        snapshot: LapSnapshot = self.session.get_snapshot(self.current_lap)

        for driver in snapshot.drivers:
            pos_str = f"P{driver.position}"
            tire = compound_badge(driver.compound)
            if self.gap_mode == "interval":
                gap = driver.interval
            else:
                gap = driver.gap_to_leader
            if driver.is_fastest_lap:
                lap_time = f"[bold purple]{driver.lap_time}[/]"
            else:
                lap_time = driver.lap_time
            color = team_color(driver.team)

            table.add_row(
                pos_str,
                f"[{color}]{driver.driver_code}[/]  [dim]{driver.full_name}[/]",
                f"[{color}]{driver.team}[/]",
                tire,
                gap,
                lap_time,
            )

    BINDINGS = [
        Binding("right", "next_lap", "Next Lap"),
        Binding("left", "prev_lap", "Prev Lap"),
        Binding("t", "toggle_gap", "Toggle Gap Mode"),
        Binding("q", "quit", "Quit"),
    ]

    def _lap_label(self) -> str:
        return f"Lap {self.current_lap} / {self.session.total_laps}  < > to step"

    def _gap_mode_label(self) -> str:
        if self.gap_mode == "interval":
            return "Gap mode: Interval (gap to car ahead)  [T] to toggle"
        else:
            return "Gap mode: Leader gap (gap to P1)  [T] to toggle"

    def action_next_lap(self):
        if self.current_lap < self.session.total_laps:
            self.current_lap += 1
            self._refresh_table()

    def action_prev_lap(self):
        if self.current_lap > 1:
            self.current_lap -= 1
            self._refresh_table()

    def action_toggle_gap(self):
        if self.gap_mode == "interval":
            self.gap_mode = "leader"
        else:
            self.gap_mode = "interval"
        self._refresh_table()


if __name__ == "__main__":
    app = PitwallApp()
    app.run()
