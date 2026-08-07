from fastapi import APIRouter, HTTPException
from app.schemas.requests import StrategyPredictionRequest
from app.schemas.responses import StrategyPredictionResponse, StrategyResult, StintBreakdown
from app.ml.inference import get_track_row, laptime_columns
from app.ml.strategy_engine import evaluate_strategy, CANDIDATE_STRATEGIES

router = APIRouter()


@router.post("/predict/strategy", response_model=StrategyPredictionResponse)
def predict_strategy_endpoint(request: StrategyPredictionRequest):
    try:
        track_row = get_track_row(request.event_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    results = []
    for strategy in CANDIDATE_STRATEGIES:
        total_time, breakdown, pit_loss = evaluate_strategy(
            strategy, request.race_laps, request.driver, track_row,
            request.track_temp, request.air_temp, laptime_columns
        )
        results.append(StrategyResult(
            strategy_name=strategy['name'],
            predicted_total_time_seconds=total_time,
            pit_loss_seconds=pit_loss,
            stint_breakdown=[StintBreakdown(**s) for s in breakdown]
        ))

    results.sort(key=lambda r: r.predicted_total_time_seconds)

    return StrategyPredictionResponse(
        event_name=request.event_name,
        driver=request.driver,
        results=results
    )