import pandas as pd
import fastf1

# 1. Enable caching to avoid rate limits
fastf1.Cache.enable_cache('f1_2023_interval')  # Change the path as needed

def export_season_gaps(year):
    all_gaps = []
    # 2. Get schedule and filter to official races
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule['EventFormat'] != 'testing']
    
    for _, event in races.iterrows():
        print(f"Processing {event['EventName']}...")
        try:
            # 3. Load race laps
            session = fastf1.get_session(year, event['EventName'], 'R')
            session.load(laps=True, telemetry=False, weather=False)
            laps = session.laps
            
            # 4. Calculate gaps relative to the session time ('Time')
            for lap_num in laps['LapNumber'].unique():
                lap_data = laps[laps['LapNumber'] == lap_num]
                leader_time = lap_data.sort_values(by='Position').iloc[0]['Time']
                
                for _, row in lap_data.iterrows():
                    if pd.isnull(row['Time']): continue
                    
                    # Calculate gap (Seconds)
                    gap = (row['Time'] - leader_time).total_seconds()
                    all_gaps.append({
                        'Event': event['EventName'], 'Lap': lap_num,
                        'Driver': row['Driver'], 'GapToLeader_Secs': gap
                    })
        except Exception as e: print(f"Error {event['EventName']}: {e}")

    # 5. Export results
    pd.DataFrame(all_gaps).to_csv(f"f1_{year}_gaps.csv", index=False)

export_season_gaps(2023)