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

    # NOTE: track_temp/air_temp aren't in OvertakePredictionRequest yet — see below
    feature_row = build_overtake_feature_row(
        request.gap_to_car_ahead, request.tyre_life_delta, request.pace_delta,
        request.same_compound, track_row, request.track_temp, request.air_temp,
        overtake_columns
    )
    prediction = predict_overtake_probability(feature_row)
    return OvertakePredictionResponse(overtake_probability=prediction)