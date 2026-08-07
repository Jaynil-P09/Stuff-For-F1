import pandas as pd


def build_laptime_feature_row(compound, tyre_life, driver, track_row,
                                 track_temp, air_temp, model_columns):
    raw_row = {
        'TyreLife': tyre_life,
        'FreshTyre': tyre_life <= 1,
        'TrackTemp': track_temp,
        'AirTemp': air_temp,
        'LapNumber': tyre_life,
        'CircuitLength_km': track_row['CircuitLength_km'],
        'NumCorners': track_row['NumCorners'],
        'NumDRSZones': track_row['NumDRSZones'],
        'AvgSpeed_kmh': track_row['AvgSpeed_kmh'],
        'ElevationChange_m': track_row['ElevationChange_m'],
    }
    df_row = pd.DataFrame([raw_row])
    df_row['Compound'] = compound
    df_row['Driver'] = driver
    df_row['TrackDirection'] = track_row['TrackDirection']
    df_row['DownforceLevel'] = track_row['DownforceLevel']

    df_row = pd.get_dummies(df_row, columns=['Compound', 'Driver', 'TrackDirection', 'DownforceLevel'])
    df_row = df_row.reindex(columns=model_columns, fill_value=0)
    return df_row


def build_degradation_feature_row(compound, tyre_life, driver, track_row,
                                     track_temp, air_temp, model_columns):
    # Note: no LapNumber here — Tire Degradation notebook never used it as a feature
    raw_row = {
        'TyreLife': tyre_life,
        'FreshTyre': tyre_life <= 1,
        'TrackTemp': track_temp,
        'AirTemp': air_temp,
        'CircuitLength_km': track_row['CircuitLength_km'],
        'NumCorners': track_row['NumCorners'],
        'NumDRSZones': track_row['NumDRSZones'],
        'AvgSpeed_kmh': track_row['AvgSpeed_kmh'],
        'ElevationChange_m': track_row['ElevationChange_m'],
    }
    df_row = pd.DataFrame([raw_row])
    df_row['Compound'] = compound
    df_row['Driver'] = driver
    df_row['TrackDirection'] = track_row['TrackDirection']
    df_row['DownforceLevel'] = track_row['DownforceLevel']

    df_row = pd.get_dummies(df_row, columns=['Compound', 'Driver', 'TrackDirection', 'DownforceLevel'])
    df_row = df_row.reindex(columns=model_columns, fill_value=0)
    return df_row


def build_overtake_feature_row(gap_to_car_ahead, tyre_life_delta, pace_delta, same_compound,
                                  track_row, track_temp, air_temp, model_columns):
    # Note: this model's features are already RELATIVE (deltas), computed upstream by the
    # caller — unlike laptime/degradation, there's no per-driver tire/compound lookup here,
    # the caller (endpoint) is responsible for supplying pre-computed deltas.
    raw_row = {
        'GapToCarAhead_Secs': gap_to_car_ahead,
        'TyreLife_Delta': tyre_life_delta,
        'Pace_Delta': pace_delta,
        'SameCompound': int(same_compound),
        'TrackTemp': track_temp,
        'AirTemp': air_temp,
        'CircuitLength_km': track_row['CircuitLength_km'],
        'NumCorners': track_row['NumCorners'],
        'NumDRSZones': track_row['NumDRSZones'],
        'AvgSpeed_kmh': track_row['AvgSpeed_kmh'],
    }
    df_row = pd.DataFrame([raw_row])
    df_row['DownforceLevel'] = track_row['DownforceLevel']

    df_row = pd.get_dummies(df_row, columns=['DownforceLevel'])
    df_row = df_row.reindex(columns=model_columns, fill_value=0)
    return df_row