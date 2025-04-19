import statsapi
import pandas as pd
import time

# Configuration: Set your season dates.
start_date = "2023-03-30"
end_date = "2023-10-01"

# Fetch the season schedule
print(f"Fetching schedule from {start_date} to {end_date} ...")
schedule = statsapi.schedule(start_date=start_date, end_date=end_date)

# List to accumulate each team’s boxscore row
boxscore_rows = []

# Loop over each game in the schedule.
for game in schedule:
    # The game identifier is usually stored as 'game_id' (or 'gamePk' in some cases).
    gamePk = game.get("game_id", None) or game.get("gamePk", None)
    if not gamePk:
        continue  # Skip if no game ID is present
    
    # Fetch the boxscore for this game.
    try:
        boxscore = statsapi.boxscore(gamePk)
    except Exception as e:
        print(f"Error fetching boxscore for game {gamePk}: {e}")
        continue

    # Loop through the teams (usually under "teams" with "home" and "away" keys)
    teams_data = boxscore.get("teams", {})
    for side in ["home", "away"]:
        team_box = teams_data.get(side, {})
        team_info = team_box.get("team", {})

        # Extract example statistics.
        # The exact structure can vary; below are common keys.
        runs = team_box.get("teamStats", {}).get("batting", {}).get("runs")
        hits = team_box.get("teamStats", {}).get("batting", {}).get("hits")
        errors = team_box.get("teamStats", {}).get("fielding", {}).get("errors")

        # Build a row with the relevant information.
        row = {
            "gamePk": gamePk,
            "date": game.get("game_date"),  # May need to adjust key name based on schedule data.
            "home_or_away": side,
            "team_id": team_info.get("id"),
            "team_name": team_info.get("name"),
            "runs": runs,
            "hits": hits,
            "errors": errors,
            # Add additional fields as needed.
        }
        boxscore_rows.append(row)

    # Be respectful to the API; pause briefly between requests.
    time.sleep(0.2)

# Convert the results to a Pandas DataFrame.
df_boxscores = pd.DataFrame(boxscore_rows)

# Optionally sort the DataFrame (e.g., by date and team name)
df_boxscores.sort_values(by=["date", "team_name"], inplace=True)

# Display the first few rows of the DataFrame
print(df_boxscores.head())

# Save the DataFrame to CSV if desired.
output_file = "2023_boxscores_by_team.csv"
df_boxscores.to_csv(output_file, index=False)
print(f"Boxscore data saved to {output_file}")
