from pydantic import BaseModel
from typing import List


class LapTimePredictionResponse(BaseModel):
    predicted_lap_time_seconds: float


class DegradationPredictionResponse(BaseModel):
    predicted_degradation_delta_seconds: float


class OvertakePredictionResponse(BaseModel):
    overtake_probability: float


class StintBreakdown(BaseModel):
    compound: str
    laps: int
    stint_time_seconds: float


class StrategyResult(BaseModel):
    strategy_name: str
    predicted_total_time_seconds: float
    pit_loss_seconds: float
    stint_breakdown: List[StintBreakdown]


class StrategyPredictionResponse(BaseModel):
    event_name: str
    driver: str
    results: List[StrategyResult]