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


def _format_gap(seconds: float | None, is_leader: bool) -> str:
    if is_leader:
        return "LEADER"
    if seconds is None or pd.isna(seconds):
        return "--"
    if seconds >= 60:
        laps = int(abs(seconds) // 60)
        if laps > 1:
            return f"+{laps} LAP{'S'}"
        else:
            return f"+{laps} LAP{''}"
    return f"+{seconds:.3f}s"


def _format_lap_time(td) -> str:
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
        self._drivers = self._build_driver_info(session)
        self.total_laps = int(self._laps["LapNumber"].max())
        self._snapshots: dict[int, LapSnapshot] = {}
        self._build_all_snapshots()

    def _build_driver_info(self, session) -> dict:
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

        for lap_num in range(1, self.total_laps + 1):
            lap_slice = laps[laps["LapNumber"] <= lap_num]
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
            if not latest.empty:
                leader_code = latest.iloc[0]["Driver"]
            else:
                leader_code = None
            leader_time = cumulative_times.get(leader_code)

            driver_states = []

            for idx, row in latest.iterrows():
                code = row["Driver"]
                if pd.notna(row["Position"]):
                    pos = int(row["Position"])
                else:
                    pos = idx + 1
                is_leader = pos == 1

                # gap to leader
                driver_time = cumulative_times.get(code)
                if is_leader:
                    gap_to_leader_str = "LEADER"
                elif driver_time is not None and leader_time is not None:
                    gap_seconds = (driver_time - leader_time).total_seconds()
                    gap_to_leader_str = _format_gap(gap_seconds, False)
                else:
                    gap_to_leader_str = "--"

                # interval
                if is_leader:
                    interval_str = "LEADER"
                elif idx > 0:
                    ahead_code = latest.iloc[idx - 1]["Driver"]
                    ahead_time = cumulative_times.get(ahead_code)
                    if driver_time is not None and ahead_time is not None:
                        interval_seconds = (driver_time - ahead_time).total_seconds()
                        interval_str = _format_gap(interval_seconds, False)
                    else:
                        interval_str = "--"
                else:
                    interval_str = "--"

                # lap time
                lap_time_str = _format_lap_time(row.get("LapTime"))

                # tire compound
                compound = row.get("Compound", "UNKNOWN")
                if pd.isna(compound):
                    compound = "?"

                # fastest lap
                fastest = False
                if pd.notna(row.get("IsPersonalBest:")):
                    fastest = bool(row["IsPersonalBest"])

                info = self._drivers.get(code, {})

                driver_states.append(
                    DriverLapState(
                        position=pos,
                        driver_code=code,
                        full_name=info.get("full_name", code),
                        team=info.get("team", "Unknown"),
                        compound=str(compound),
                        gap_to_leader=gap_to_leader_str,
                        interval=interval_str,
                        lap_time=lap_time_str,
                        is_fastest_lap=fastest,
                    )
                )

            self._snapshots[lap_num] = LapSnapshot(
                lap_number=lap_num,
                total_laps=self.total_laps,
                drivers=driver_states,
            )

    def get_snapshot(self, lap: int) -> LapSnapshot:
        lap = max(1, min(lap, self.total_laps))
        return self._snapshots[lap]


if __name__ == "__main__":
    enable_cache()
    session = load_session(2024, "Monza")
    print(f"{session.race_name} - {session.total_laps}")
    snapshot = session.get_snapshot(1)
    for driver in snapshot.drivers:
        print(
            f"{driver.position}, {driver.driver_code}, {driver.gap_to_leader}, {driver.interval}, {driver.lap_time}"
        )
