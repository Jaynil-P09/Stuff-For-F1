import fastf1
import pandas as pd
import os

os.makedirs('fastf1_cache', exist_ok=True)
fastf1.Cache.enable_cache('fastf1_cache')

year = 2025
all_season_laps = []

schedule = fastf1.get_event_schedule(year)
gps = schedule[schedule['EventFormat'] != 'testing']

for index, event in gps.iterrows():
    gp_name = event['EventName']
    print(f"Processing {gp_name}...")

    try:
        session = fastf1.get_session(year, gp_name, 'R')
        session.load(laps=True, telemetry=False, weather=False)

        laps_df = session.laps.copy()

        laps_df['RoundNumber'] = event['RoundNumber']
        laps_df['EventName'] = gp_name

        all_season_laps.append(laps_df)
    except Exception as e:
        print(f"Failed to process {gp_name}: {e}")

if all_season_laps:
    final_laps_df = pd.concat(all_season_laps, ignore_index=True)
    final_laps_df.to_csv(f'f1_{year}_all_driver_laps.csv', index=False)
    print(f"All driver laps for {year} saved to f1_{year}_all_driver_laps.csv")
        

        
