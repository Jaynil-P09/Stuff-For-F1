from fastapi import APIRouter, HTTPException
from app.schemas.requests import DegradationPredictionRequest
from app.schemas.responses import DegradationPredictionResponse
from app.ml.inference import get_track_row, predict_degradation, degradation_columns
from app.ml.feature_builder import build_degradation_feature_row

router = APIRouter()


@router.post("/predict/degradation", response_model=DegradationPredictionResponse)
def predict_degradation_endpoint(request: DegradationPredictionRequest):
    try:
        track_row = get_track_row(request.event_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    feature_row = build_degradation_feature_row(
        request.compound, request.tyre_life, request.driver, track_row,
        request.track_temp, request.air_temp, degradation_columns
    )
    prediction = predict_degradation(feature_row)
    return DegradationPredictionResponse(predicted_degradation_delta_seconds=prediction)