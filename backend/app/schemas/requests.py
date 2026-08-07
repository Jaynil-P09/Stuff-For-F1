from pydantic import BaseModel


class LapTimePredictionRequest(BaseModel):
    driver: str
    event_name: str
    compound: str
    tyre_life: int
    track_temp: float
    air_temp: float


class DegradationPredictionRequest(BaseModel):
    driver: str
    event_name: str
    compound: str
    tyre_life: int
    track_temp: float
    air_temp: float


class OvertakePredictionRequest(BaseModel):
    driver: str
    event_name: str
    gap_to_car_ahead: float
    tyre_life_delta: float
    pace_delta: float
    same_compound: bool
    track_temp: float
    air_temp: float

class StrategyPredictionRequest(BaseModel):
    driver: str
    event_name: str
    race_laps: int
    track_temp: float
    air_temp: float