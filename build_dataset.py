import pandas as pd

laps_df = pd.read_csv('f1_2023_all_driver_laps.csv')
gaps_df = pd.read_csv('f1_2023_gaps.csv')
weather_df = pd.read_csv('f1_2023_weather.csv')

gaps_df = gaps_df.sort_values(['EventName', 'Lap', 'GapToLeader_Secs'])
gaps_df['GapToCarAhead_Secs'] = gaps_df.groupby(['EventName', 'Lap'])['GapToLeader_Secs'].diff()

laps_df = laps_df.merge(gaps_df[['EventName', 'Lap', 'Driver', 'GapToCarAhead_Secs']], left_on=['EventName', 'LapNumber', 'Driver'], right_on=['EventName', 'Lap', 'Driver'], how='left')

laps_df['Time'] = pd.to_timedelta(laps_df['Time'])
weather_df['Time'] = pd.to_timedelta(weather_df['Time'])
laps_df = laps_df.sort_values(['Time'])
weather_df = weather_df.sort_values(['Time'])

weather_cols = ['EventName', 'Time', 'AirTemp', 'Humidity', 'Pressure', 'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed']

merged_df = pd.merge_asof(laps_df, weather_df[weather_cols], on='Time', by='EventName', direction='backward')

merged_df.to_csv('f1_2023_merged.csv', index=False)

sample = merged_df[merged_df['EventName'] == 'Bahrain Grand Prix'].sort_values(['LapNumber', 'Position']).head(20)
print(sample[['EventName', 'LapNumber', 'Driver', 'Position', 'GapToCarAhead_Secs', 'TrackTemp', 'AirTemp', 'Time']])
print(len(laps_df), len(merged_df))