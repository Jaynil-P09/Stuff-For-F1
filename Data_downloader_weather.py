import fastf1
import pandas as pd

# 1. Set up caching (highly recommended)
fastf1.Cache.enable_cache('f1_2023_weather') 

# Define your target season
season_year = 2025
session_type = 'R'  # 'R' for Race, 'Q' for Qualifying, 'FP1' for Practice 1

# 2. Get the entire season schedule
schedule = fastf1.get_event_schedule(season_year)

# Filter out testing events to only keep official rounds
rounds = schedule[schedule['RoundNumber'] > 0]

all_season_weather = []

# 3. Loop through every round
for _, row in rounds.iterrows():
    round_num = row['RoundNumber']
    event_name = row['EventName']
    
    print(f"Loading weather for Round {round_num}: {event_name}...")
    
    try:
        # Get the specific session
        session = fastf1.get_session(season_year, round_num, session_type)
        
        # Load only the weather data to minimize download times
        session.load(laps=False, telemetry=False, weather=True, messages=False)
        
        # Extract weather DataFrame
        weather_df = session.weather_data.copy()
        
        # Append metadata tracking columns
        weather_df['Year'] = season_year
        weather_df['RoundNumber'] = round_num
        weather_df['EventName'] = event_name
        
        all_season_weather.append(weather_df)
        
    except Exception as e:
        print(f"Could not load data for {event_name}: {e}")

# 4. Combine and export the final dataset
if all_season_weather:
    final_weather_df = pd.concat(all_season_weather, ignore_index=True)
    
    # Save to CSV
    csv_filename = f"f1_{season_year}_season_weather.csv"
    final_weather_df.to_csv(csv_filename, index=False)
    print(f"Successfully exported whole season weather data to {csv_filename}!")
else:
    print("No weather data compiled.")
