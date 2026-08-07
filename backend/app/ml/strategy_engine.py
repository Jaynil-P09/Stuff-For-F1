import pandas as pd
from app.ml.inference import predict_laptime
from app.ml.feature_builder import build_laptime_feature_row


def simulate_stint(compound, start_tyre_life, n_laps, driver, track_row,
                    track_temp, air_temp, model_columns):
    total_time = 0
    lap_times = []
    for lap_offset in range(n_laps):
        tyre_life = start_tyre_life + lap_offset
        row = build_laptime_feature_row(compound, tyre_life, driver, track_row,
                                           track_temp, air_temp, model_columns)
        predicted_time = predict_laptime(row)
        lap_times.append(predicted_time)
        total_time += predicted_time
    return total_time, lap_times


def evaluate_strategy(strategy, race_laps, driver, track_row,
                        track_temp, air_temp, model_columns):
    total_time = 0
    laps_remaining = race_laps
    n_stints = len(strategy['stints'])
    pit_loss = track_row['PitLoss_secs']
    stint_breakdown = []

    for i, (compound, stint_length) in enumerate(strategy['stints']):
        if stint_length is None:
            stint_length = laps_remaining // (n_stints - i)
        stint_time, _ = simulate_stint(compound, 1, stint_length, driver, track_row,
                                          track_temp, air_temp, model_columns)
        total_time += stint_time
        stint_breakdown.append({
            'compound': compound,
            'laps': stint_length,
            'stint_time_seconds': stint_time
        })
        laps_remaining -= stint_length
        if i < n_stints - 1:
            total_time += pit_loss

    return total_time, stint_breakdown, pit_loss


CANDIDATE_STRATEGIES = [
    {"name": "1-Stop: Medium-Hard", "stints": [("MEDIUM", None), ("HARD", None)]},
    {"name": "1-Stop: Hard-Medium", "stints": [("HARD", None), ("MEDIUM", None)]},
    {"name": "2-Stop: Medium-Medium-Hard", "stints": [("MEDIUM", None), ("MEDIUM", None), ("HARD", None)]},
    {"name": "2-Stop: Soft-Medium-Hard", "stints": [("SOFT", None), ("MEDIUM", None), ("HARD", None)]},
]