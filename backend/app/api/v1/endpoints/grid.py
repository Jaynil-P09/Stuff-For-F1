# app/api/v1/endpoints/grid.py — NEW FILE
#
# GET /api/v1/grid                                 -> live, if a session is active
# GET /api/v1/grid?year=&event_name=&session_type=  -> explicit historical session
# If neither applies (no live session AND no historical params given), returns
# status: "no_active_session" so the frontend can prompt for a historical pick
# instead of silently guessing which past race you meant.

from fastapi import APIRouter, HTTPException
from typing import Optional
from app.ml.inference import get_track_row
from app.ml.grid_builder import (
    get_live_session, fetch_openf1_grid_state, fetch_fastf1_grid_state, build_grid_predictions,
    OPENF1_EVENT_NAME_MAP,
)

router = APIRouter()


@router.get("/grid")
def get_grid(year: Optional[int] = None, event_name: Optional[str] = None, session_type: Optional[str] = None):
    live_session = None if (year or event_name or session_type) else get_live_session()

    if live_session:
        driver_states, track_temp, air_temp = fetch_openf1_grid_state(live_session["session_key"])
        source = "live"
        circuit = live_session.get("circuit_short_name", "")
        resolved_event = OPENF1_EVENT_NAME_MAP.get(circuit, circuit)
    elif year and event_name and session_type:
        driver_states, track_temp, air_temp = fetch_fastf1_grid_state(year, event_name, session_type)
        source = "historical"
        resolved_event = event_name
    else:
        return {
            "status": "no_active_session",
            "message": "No live session right now. Pass year, event_name and session_type to view a past session.",
        }

    try:
        track_row = get_track_row(resolved_event)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"{e} (source={source}, resolved_event='{resolved_event}')")

    predictions = build_grid_predictions(driver_states, track_row, track_temp, air_temp)
    return {"status": "ok", "source": source, "event_name": resolved_event, "drivers": predictions}
