import os
import pandas as pd

# Define folder paths
roster_folder = "2024_roster"
hw_roster_folder = "2024_hw_roster"
output_folder = "2024_hw_roster_updated"

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Log available files in the roster folder
roster_files = os.listdir(roster_folder)
print("Files in 2024_roster folder:", roster_files)

# Mapping of team names to file names in 2024_roster
team_file_mapping = {
    "Arizona Cardinals": "arizona_cardinals_player_data.csv",
    "Atlanta Falcons": "atlanta_falcons_player_data.csv",
    "Baltimore Ravens": "baltimore_ravens_player_data.csv",
    "Buffalo Bills": "buffalo_bills_player_data.csv",
    "Carolina Panthers": "carolina_panthers_player_data.csv",
    "Chicago Bears": "chicago_bears_player_data.csv",
    "Cincinnati Bengals": "cincinnati_bengals_player_data.csv",
    "Cleveland Browns": "cleveland_browns_player_data.csv",
    "Dallas Cowboys": "dallas_cowboys_player_data.csv",
    "Denver Broncos": "denver_broncos_player_data.csv",
    "Detroit Lions": "detroit_lions_player_data.csv",
    "Green Bay Packers": "green_bay_packers_player_data.csv",
    "Houston Texans": "houston_texans_player_data.csv",
    "Indianapolis Colts": "indianapolis_colts_player_data.csv",
    "Jacksonville Jaguars": "jacksonville_jaguars_player_data.csv",
    "Kansas City Chiefs": "kansas_city_chiefs_player_data.csv",
    "Las Vegas Raiders": "las_vegas_raiders_player_data.csv",
    "Los Angeles Chargers": "los_angeles_chargers_player_data.csv",
    "Los Angeles Rams": "los_angeles_rams_player_data.csv",
    "Miami Dolphins": "miami_dolphins_player_data.csv",
    "Minnesota Vikings": "minnesota_vikings_player_data.csv",
    "New England Patriots": "new_england_patriots_player_data.csv",
    "New Orleans Saints": "new_orleans_saints_player_data.csv",
    "New York Giants": "new_york_giants_player_data.csv",
    "New York Jets": "new_york_jets_player_data.csv",
    "Philadelphia Eagles": "philadelphia_eagles_player_data.csv",
    "Pittsburgh Steelers": "pittsburgh_steelers_player_data.csv",
    "San Francisco 49ers": "san_francisco_49ers_player_data.csv",
    "Seattle Seahawks": "seattle_seahawks_player_data.csv",
    "Tampa Bay Buccaneers": "tampa_bay_buccaneers_player_data.csv",
    "Tennessee Titans": "tennessee_titans_player_data.csv",
    "Washington Commanders": "washington_commanders_player_data.csv",
}

# Process each file in the hw_roster folder
for hw_file in os.listdir(hw_roster_folder):
    if hw_file.endswith("_roster.csv"):
        # Extract the team name from the hw_roster file name
        team_name = hw_file.replace("_roster.csv", "").replace("_", " ")

        # Read the hw_roster file
        hw_path = os.path.join(hw_roster_folder, hw_file)
        hw_df = pd.read_csv(hw_path)

        # Standardize column names in hw_roster
        hw_df.rename(
            columns={
                "Pos": "Position",
                "Height": "Ht",
                "Weight": "Wt",
                "Player": "Name",
            },
            inplace=True,
        )

        # Get the corresponding roster file
        roster_file = team_file_mapping.get(team_name)
        if roster_file:
            roster_path = os.path.join(roster_folder, roster_file)
            if os.path.exists(roster_path):
                # Read the roster file
                roster_df = pd.read_csv(roster_path)

                # Standardize column names in roster
                roster_df.rename(
                    columns={
                        "Position": "Pos",
                        "Height": "Ht",
                        "Weight": "Wt",
                    },
                    inplace=True,
                )

                # Merge data based on the player's name
                merged_df = pd.merge(
                    hw_df,
                    roster_df[['Name', 'Arms', 'Hands']],
                    on='Name',
                    how='left'
                )

                # Save the updated hw_roster file
                output_path = os.path.join(output_folder, hw_file)
                merged_df.to_csv(output_path, index=False)
                print(f"Updated file saved: {output_path}")
            else:
                print(f"Roster file not found for team: {team_name} ({roster_file})")
        else:
            print(f"No mapping found for team: {team_name}")
