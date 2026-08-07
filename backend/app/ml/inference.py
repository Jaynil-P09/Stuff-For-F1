import joblib
import pandas as pd
from app.core.config import (
    LAPTTIME_MODEL_PATH,
    LAPTTIME_COLUMNS_PATH,
    DEGRADATION_MODEL_PATH,
    DEGRADATION_COLUMNS_PATH,
    OVERTAKE_MODEL_PATH,
    OVERTAKE_COLUMNS_PATH,
    TRACK_CHARACTERISTICS_CSV,
)

laptime_model = joblib.load(LAPTTIME_MODEL_PATH)
laptime_columns = joblib.load(LAPTTIME_COLUMNS_PATH)
degradation_model = joblib.load(DEGRADATION_MODEL_PATH)
degradation_columns = joblib.load(DEGRADATION_COLUMNS_PATH)
overtake_model = joblib.load(OVERTAKE_MODEL_PATH)
overtake_columns = joblib.load(OVERTAKE_COLUMNS_PATH)

track_df = pd.read_csv(TRACK_CHARACTERISTICS_CSV)
track_df['EventName'] = track_df['EventName'].str.strip()
track_df['TrackDirection'] = track_df['TrackDirection'].str.strip()

def get_track_row(event_name: str) -> pd.Series:
    match = track_df[track_df['EventName'].str == event_name]
    if match.empty:
        raise ValueError(f"Unknown event: {event_name}")
    return match.iloc[0]

def predict_laptime(feature_row: pd.DataFrame) -> float:
    return lapttime_model.predict(feature_row)[0]

def predict_degradation(feature_row: pd.DataFrame) -> float:
    return degradation_model.predict(feature_row)[0]

def predict_overtake_probability(feature_row: pd.DataFrame) -> float:
    return overtake_model.predict_proba(feature_row)[0, 1]