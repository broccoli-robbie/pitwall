import fastf1
import pandas as pd
from pathlib import Path
from dataclasses import dataclass


CACHE_DIR = Path.home() / ".cache" / "pitwall"


def enable_cache() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(CACHE_DIR))


@dataclass
class DriverLapState:
    position: int
    driver_code: str
    full_name: str
    team: str
    compound: str
    gap_to_leader: str
    interval: str
    lap_time: str
    is_fastest_lap: bool


@dataclass
class LapSnapshot:
    lap_number: int
    total_laps: int
    drivers: list[DriverLapState]


def format_gap(seconds: float | None, is_leader: bool) -> str:
    if is_leader:
        return "LEADER"
    if seconds is None or pd.isna(seconds):
        return "--"
    if seconds >= 60:
        laps = int(abs(seconds) // 60)
        return f"+{laps} LAP{'S' if laps > 1 else ''}"
    return f"+{seconds:.3f}s"


def format_lap_time(td) -> str:
    if td is None or pd.isna(td):
        return "--"
    total_seconds = td.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes}: {seconds:06.3f}"


def load_session(year: int, race: str) -> "SessionData":
    enable_cache()
    session = fastf1.get_session(year, race, "R")
    session.load(telemetry=False, weather=False, messages=False)
    return SessionData(session)


class SessionData:
    def __init__(self, session) -> None:
        self.session = session
        self.race_name = session.event["EventName"]
        self.year = session.event.year
        self._laps = session.laps
        self._drivers = self._build_driver_info()
        self.total_laps = int(self._laps["LapNumber"].max())
        self._snapshots: dict[int, LapSnapshot] = {}
        self._build_all_snapshots()

    def _build_driver_info(self) -> dict:
        drivers = {}
        for drv in self.session.drivers:
            info = session.get_driver(drv)
            drivers[info["Abbreviation"]] = {
                "full_name": f"{info['FirstName']} {info['LastName']}",
                "team": info["TeamName"],
            }
        return drivers

    def _build_all_snapshots(self):
        laps = self._laps.copy()

        for lap_number in range(1, self.total_laps + 1):
            lap_slice = laps[laps["LapNumber"] <= lap_number]
            if lap_slice.empty:
                continue

            # for each driver, get latest lap
            latest = (
                lap_slice.sort_values("LapNumber")
                .groupby("Driver", as_index=False)
                .last()
            )

            # sort by position
            latest = latest.sort_values("Position").reset_index(drop=True)

            # build cumulative race time for gaps
            leader_time = None
            cumulative_times = {}
            for _, row in latest.iterrows():
                if pd.notna(row.get("Time")):
                    cumulative_times[row["Driver"]] = row["Time"]

            # p1 driver
            leader_code = latest.iloc[0]["Driver"] if not latest.empty else None
            leader_time = cumulative_times.get(leader_code)

            driver_states = []
