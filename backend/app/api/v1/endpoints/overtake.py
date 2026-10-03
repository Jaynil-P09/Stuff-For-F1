# INFERRED — I have not seen your actual app/api/v1/endpoints/overtake.py.
# build_overtake_feature_row's docstring says deltas are computed upstream by
# the caller — I'm assuming the caller is "whoever sends this request" (i.e.
# the client computes gap/tyre-life/pace deltas), since no driver-standings
# lookup exists anywhere else in the code you've shown me. If your actual
# overtake.py computes these deltas server-side instead, this needs rework,
# not just a schema tweak.

from fastapi import APIRouter, HTTPException
from app.schemas.requests import OvertakePredictionRequest
from app.schemas.responses import OvertakePredictionResponse
from app.ml.inference import get_track_row, predict_overtake_probability, overtake_columns
from app.ml.feature_builder import build_overtake_feature_row

router = APIRouter()


@router.post("/predict/overtake", response_model=OvertakePredictionResponse)
def predict_overtake_endpoint(request: OvertakePredictionRequest):
    try:
        track_row = get_track_row(request.event_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    feature_row = build_overtake_feature_row(
        request.gap_to_car_ahead, request.tyre_life_delta, request.pace_delta,
        request.same_compound, track_row, request.track_temp, request.air_temp,
        overtake_columns
    )
    probability = predict_overtake_probability(feature_row)
    return OvertakePredictionResponse(overtake_probability=probability)