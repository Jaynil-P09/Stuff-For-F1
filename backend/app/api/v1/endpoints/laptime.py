from fastapi import APIRouter, HTTPException
from app.schemas.requests import LapTimePredictionRequest
from app.schemas.responses import LapTimePredictionResponse
from app.ml.inference import get_track_row, predict_laptime, laptime_columns
from app.ml.feature_builder import build_laptime_feature_row

router = APIRouter()


@router.post("/predict/laptime", response_model=LapTimePredictionResponse)
def predict_laptime_endpoint(request: LapTimePredictionRequest):
    try:
        track_row = get_track_row(request.event_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    feature_row = build_laptime_feature_row(
        request.compound, request.tyre_life, request.driver, track_row,
        request.track_temp, request.air_temp, laptime_columns
    )
    prediction = predict_laptime(feature_row)
    return LapTimePredictionResponse(predicted_lap_time_seconds=prediction)