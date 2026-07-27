import pandas as pd

laps_df = pd.read_csv('f1_2023_all_driver_laps.csv')
gaps_df = pd.read_csv('f1_2023_gaps.csv')
weather_df = pd.read_csv('f1_2023_weather.csv')
merged_df = pd.read_csv('f1_2023_merged.csv')

print(merged_df['TrackStatus'].unique())
print(merged_df['TrackStatus'].value_counts())
merged_df['TrackStatus'] = merged_df['TrackStatus'].astype(str)
merged_df['is_green_flag'] = merged_df['TrackStatus'].apply(lambda x: set(x) == {'1'})

print(merged_df['is_green_flag'].value_counts())

merged_df['is_pit_lap'] = merged_df['PitOutTime'].notna() | merged_df['PitInTime'].notna()
merged_df['is_clean_lap'] = merged_df['is_green_flag'] & ~merged_df['is_pit_lap']

print(merged_df['is_clean_lap'].value_counts())

sample = merged_df[merged_df['EventName'] == 'Bahrain Grand Prix'].sort_values(['Driver', 'LapNumber'])
print(sample[sample['Driver'] == 'VER'][['LapNumber', 'Stint', 'Compound', 'TyreLife', 'PitInTime', 'PitOutTime']].head(30))

lap_model_df = merged_df[merged_df['is_clean_lap'] == True].copy()
lap_model_df['LapTime_Seconds'] = pd.to_timedelta(lap_model_df['LapTime']).dt.total_seconds()

lap_model_df.to_csv('f1_2023_lap_model_data.csv', index=False)