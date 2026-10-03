"""
app/ml/grid_builder.py — NEW FILE

Builds a full-grid prediction view, live or historical, by fetching session
state and running every driver through the existing laptime/degradation/
overtake predictors. Reuses feature_builder.py and inference.py as-is —
no duplicated feature logic.

CONFIRMED (verified against OpenF1 docs during this build):
  - /intervals fields: interval (gap to car ahead, secs), gap_to_leader
  - /stints fields: compound, tyre_age_at_start
  - session_key="latest" resolves to the current/most recent session

ASSUMED, NOT DIRECTLY VERIFIED — check your first real response:
  - /weather field names: air_temperature, track_temperature
  - /sessions field names: date_start, date_end (ISO 8601, used to decide
    whether "latest" is actually in progress right now)

UNRESOLVED — this will not work end-to-end until addressed:
  - OpenF1 identifies races by circuit_short_name / meeting_key, not the
    EventName strings in your track_characteristics.csv. OPENF1_EVENT_NAME_MAP
    below is an empty stub. Until it's filled in, get_track_row() will raise
    "Unknown event" for live sessions even when everything else works.
  - Historical mode returns each driver's state at the END of the session
    (last lap recorded), not a scrubbable "state as of lap N". That's a
    deliberate simplification to ship something testable, not an oversight —
    push back if you want per-lap scrubbing instead.
  - Historical gap_to_car_ahead is not reconstructed (your build_dataset.py
    does this via the GapToLeader diff logic, but that's a batch CSV process,
    not something fetch_fastf1_grid_state does live) — overtake predictions
    will be skipped for historical mode until this is wired up.
"""

import requests
import fastf1
from datetime import datetime, timezone
from app.ml.inference import (
    get_track_row, laptime_columns, degradation_columns, overtake_columns,
    predict_laptime, predict_degradation, predict_overtake_probability,
)
from app.ml.feature_builder import (
    build_laptime_feature_row, build_degradation_feature_row, build_overtake_feature_row,
)

OPENF1_BASE = "https://api.openf1.org/v1"

# Fill this in as you discover OpenF1 circuit_short_name <-> your EventName
# mismatches. Left empty deliberately — I don't have your actual CSV values.
OPENF1_EVENT_NAME_MAP = {
    # "Monza": "Italian Grand Prix",
}


def _get(path, **params):
    resp = requests.get(f"{OPENF1_BASE}/{path}", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_live_session():
    """Returns the OpenF1 session dict if one is currently in progress
    (now falls between date_start and date_end), else None."""
    sessions = _get("sessions", session_key="latest")
    if not sessions:
        return None
    session = sessions[0]
    now = datetime.now(timezone.utc)
    start = datetime.fromisoformat(session["date_start"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(session["date_end"].replace("Z", "+00:00"))
    return session if start <= now <= end else None


def fetch_openf1_grid_state(session_key):
    """Four calls total regardless of grid size — OpenF1 endpoints are
    session-scoped, not per-driver, so this stays well inside the free-tier
    rate limit (3 req/s / 30 req/min)."""
    drivers = _get("drivers", session_key=session_key)
    intervals = _get("intervals", session_key=session_key)
    stints = _get("stints", session_key=session_key)
    weather = _get("weather", session_key=session_key)
    laps = _get("laps", session_key=session_key)

    latest_weather = weather[-1] if weather else {}
    track_temp = latest_weather.get("track_temperature")
    air_temp = latest_weather.get("air_temperature")

    state = {}
    for d in drivers:
        num = d["driver_number"]
        state[num] = {"driver": d.get("name_acronym", str(num)), "driver_number": num}

    for row in intervals:
        num = row["driver_number"]
        if num in state:
            state[num]["gap_to_car_ahead"] = row.get("interval")
            state[num]["gap_to_leader"] = row.get("gap_to_leader")

    latest_lap_by_driver = {}
    for row in laps:
        num, ln = row["driver_number"], row.get("lap_number")
        if ln is not None and (num not in latest_lap_by_driver or ln > latest_lap_by_driver[num]):
            latest_lap_by_driver[num] = ln

    stints_by_driver = {}
    for row in stints:
        stints_by_driver.setdefault(row["driver_number"], []).append(row)

    for num, driver_stints in stints_by_driver.items():
        if num not in state:
            continue
        current_stint = max(driver_stints, key=lambda s: s["stint_number"])
        current_lap = latest_lap_by_driver.get(num, current_stint["lap_start"])
        state[num]["compound"] = current_stint["compound"]
        state[num]["tyre_life"] = current_stint["tyre_age_at_start"] + max(0, current_lap - current_stint["lap_start"])

    return list(state.values()), track_temp, air_temp


def fetch_fastf1_grid_state(year, event_name, session_type):
    """Snapshot of every driver's state at the END of the session (last
    recorded lap) — not a per-lap replay. gap_to_car_ahead is NOT populated
    here (see module docstring) so overtake predictions are skipped for
    historical mode until that's wired up."""
    session = fastf1.get_session(year, event_name, session_type)
    session.load()
    laps = session.laps

    state = []
    for driver_code in laps['Driver'].unique():
        driver_laps = laps[laps['Driver'] == driver_code]
        last_lap = driver_laps.iloc[-1]
        state.append({
            "driver": driver_code,
            "compound": last_lap["Compound"],
            "tyre_life": last_lap["TyreLife"],
            "gap_to_car_ahead": None,  # not reconstructed — see docstring
            "gap_to_leader": last_lap.get("Position"),  # ordering proxy, not a real time gap
        })

    weather = session.weather_data
    track_temp = weather["TrackTemp"].iloc[-1] if not weather.empty else None
    air_temp = weather["AirTemp"].iloc[-1] if not weather.empty else None
    return state, track_temp, air_temp


def build_grid_predictions(driver_states, track_row, track_temp, air_temp):
    """Lap time + degradation for every driver with complete data. Overtake
    is computed pairwise against the car immediately ahead in running order,
    using each driver's OWN predicted lap time for pace_delta — not a second
    guess at the ahead car's actual pace."""
    ordered = sorted(
        [d for d in driver_states if d.get("gap_to_leader") is not None],
        key=lambda d: d["gap_to_leader"]
    )

    entries = []
    for d in ordered:
        if "compound" not in d or "tyre_life" not in d:
            continue  # incomplete data for this driver — skip rather than guess

        lt_row = build_laptime_feature_row(d["compound"], d["tyre_life"], d["driver"], track_row, track_temp, air_temp, laptime_columns)
        dg_row = build_degradation_feature_row(d["compound"], d["tyre_life"], d["driver"], track_row, track_temp, air_temp, degradation_columns)
        entries.append({
            "driver": d["driver"],
            "compound": d["compound"],
            "tyre_life": d["tyre_life"],
            "gap_to_car_ahead": d.get("gap_to_car_ahead"),
            "predicted_lap_time_seconds": predict_laptime(lt_row),
            "predicted_degradation": float(predict_degradation(dg_row)),
            "overtake_probability": None,
        })

    for i in range(1, len(entries)):
        behind, ahead = entries[i], entries[i - 1]
        if behind["gap_to_car_ahead"] is None:
            continue  # historical mode currently has no gap data — skip, don't fabricate
        ot_row = build_overtake_feature_row(
            behind["gap_to_car_ahead"],
            behind["tyre_life"] - ahead["tyre_life"],
            behind["predicted_lap_time_seconds"] - ahead["predicted_lap_time_seconds"],
            behind["compound"] == ahead["compound"],
            track_row, track_temp, air_temp, overtake_columns
        )
        behind["overtake_probability"] = float(predict_overtake_probability(ot_row))

    return entries
