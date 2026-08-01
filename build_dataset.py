import pandas as pd

laps_df_2023 = pd.read_csv('f1_2023_all_driver_laps.csv')
gaps_df_2023 = pd.read_csv('f1_2023_gaps.csv')
weather_df_2023 = pd.read_csv('f1_2023_season_weather.csv')

laps_df_2024 = pd.read_csv('f1_2024_all_driver_laps.csv')
gaps_df_2024 = pd.read_csv('f1_2024_gaps.csv')
weather_df_2024 = pd.read_csv('f1_2024_season_weather.csv')

laps_df_2025 = pd.read_csv('f1_2025_all_driver_laps.csv')
gaps_df_2025 = pd.read_csv('f1_2025_gaps.csv')
weather_df_2025 = pd.read_csv('f1_2025_season_weather.csv')

laps_df = pd.concat([laps_df_2023, laps_df_2024, laps_df_2025], ignore_index=True)
gaps_df = pd.concat([gaps_df_2023, gaps_df_2024, gaps_df_2025], ignore_index=True)
weather_df = pd.concat([weather_df_2023, weather_df_2024, weather_df_2025], ignore_index=True)

laps_df.to_csv('f1_laps_merged.csv', index=False)
gaps_df.to_csv('f1_gaps_merged.csv', index=False)
weather_df.to_csv('f1_weather_merged.csv', index=False)

gaps_df = gaps_df.sort_values(['EventName', 'Lap', 'GapToLeader_Secs'])
gaps_df['GapToCarAhead_Secs'] = gaps_df.groupby(['EventName', 'Lap'])['GapToLeader_Secs'].diff()

laps_df = laps_df.merge(gaps_df[['EventName', 'Lap', 'Driver', 'GapToCarAhead_Secs']], left_on=['EventName', 'LapNumber', 'Driver'], right_on=['EventName', 'Lap', 'Driver'], how='left')

laps_df['Time'] = pd.to_timedelta(laps_df['Time'])
weather_df['Time'] = pd.to_timedelta(weather_df['Time'])
laps_df = laps_df.sort_values(['Time'])
weather_df = weather_df.sort_values(['Time'])

weather_cols = ['EventName', 'Time', 'AirTemp', 'Humidity', 'Pressure', 'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed']

merged_df = pd.merge_asof(laps_df, weather_df[weather_cols], on='Time', by='EventName', direction='backward')

merged_df.to_csv('f1_merged.csv', index=False)

sample = merged_df[merged_df['EventName'] == 'Bahrain Grand Prix'].sort_values(['LapNumber', 'Position']).head(20)
print(sample[['EventName', 'LapNumber', 'Driver', 'Position', 'GapToCarAhead_Secs', 'TrackTemp', 'AirTemp', 'Time']])
print(len(laps_df), len(merged_df))