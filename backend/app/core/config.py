from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "ml" / "models"

LAPTTIME_MODEL_PATH = MODEL_DIR / "lap_time.joblib"
LAPTTIME_COLUMNS_PATH = MODEL_DIR / "lap_model_columns.joblib"
DEGRADATION_MODEL_PATH = MODEL_DIR / "tire_deg.joblib"
DEGRADATION_COLUMNS_PATH = MODEL_DIR / "tire_deg_columns.joblib"
OVERTAKE_MODEL_PATH = MODEL_DIR / "over_take.joblib"
OVERTAKE_COLUMNS_PATH = MODEL_DIR / "overtake_columns.joblib"

TRACK_CHARACTERISTICS_CSV = BASE_DIR / "ml" / "data" / "track_char.csv"

PIT_LOSS_SECONDS = 22
