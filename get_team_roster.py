import pandas as pd
import os

# Folder where the team CSVs are stored
teams_folder = "teams"
if not os.path.exists(teams_folder):
    os.makedirs(teams_folder)

# Function to extract player data and add to the corresponding team CSV
def add_player_to_team_csv(player_file, position):
    try:
        # Extract the player's name from the filename (e.g., Tyreek_Hill_career_receiving_stats.csv)
        player_name = os.path.basename(player_file).split('_career_')[0].replace('_', ' ')
        print(f"Processing player: {player_name} ({position})")
        
        # Read the player's career stats CSV
        df_player = pd.read_csv(player_file)
        
        # Check if the dataframe is empty
        if df_player.empty:
            print(f"Warning: {player_file} is empty.")
            return
        
        # Filter out rows with missing or NaN values in the TEAM column
        df_player = df_player.dropna(subset=['TEAM'])
        if df_player.empty:
            print(f"Warning: No valid team data found for {player_name}. Skipping player.")
            return
        
        # Extract the most recent team from the last row
        team_name = df_player.iloc[-1]['TEAM']
        
        print(f"Most recent team for {player_name}: {team_name}")
        
        # Format the team name for the CSV filename (e.g., "New York Jets" -> "new_york_jets")
        team_csv_filename = os.path.join(teams_folder, f"{team_name.lower().replace(' ', '_')}.csv")
        
        # Create a new DataFrame for the player with their position
        player_data = pd.DataFrame([{'Position': position, 'Name': player_name}])
        
        # Check if the team's CSV already exists
        if os.path.exists(team_csv_filename):
            print(f"File exists: {team_csv_filename}")
            # If the file exists, read it and check the number of players per position
            df_team = pd.read_csv(team_csv_filename)
            
            # Count the number of players for each position
            position_counts = df_team['Position'].value_counts()
            print(f"Current position counts for {team_name}: {position_counts}")
            
            # Handle the position limits
            if position == 'QB' and position_counts.get('QB', 0) < 2:
                df_team = pd.concat([df_team, player_data], ignore_index=True)
            elif position == 'RB' and position_counts.get('RB', 0) < 3:
                df_team = pd.concat([df_team, player_data], ignore_index=True)
            elif position == 'WR' and position_counts.get('WR', 0) < 5:
                df_team = pd.concat([df_team, player_data], ignore_index=True)
            elif position == 'K' and position_counts.get('K', 0) < 1:
                df_team = pd.concat([df_team, player_data], ignore_index=True)
            else:
                print(f"Cannot add {player_name} to {team_name} - position limit reached.")
                return
            
            # Save the updated team CSV
            df_team.to_csv(team_csv_filename, index=False)
            print(f"Updated {team_csv_filename} with {player_name}")
        else:
            print(f"Creating new file: {team_csv_filename}")
            # If the file doesn't exist, create it with the player data
            player_data.to_csv(team_csv_filename, index=False)
            print(f"Created new file {team_csv_filename} with {player_name}")
    
    except Exception as e:
        print(f"Error processing {player_file}: {e}")

# Folder where the player career stats files are located
qb_stats_folder = "qb_stats/qb_career_passing_stats"
rb_stats_folder = "rb_stats/rb_career_rushing_stats"
wr_stats_folder = "wr_stats/wr_career_receiving_stats"
kicker_stats_folder = "kicker_stats/kicker_career_stats"

# Function to process all files in a folder, including subdirectories
def process_folder(folder_path, position, file_suffix):
    for root, dirs, files in os.walk(folder_path):
        for player_file in files:
            if player_file.endswith(file_suffix):  # Match the appropriate file suffix
                player_file_path = os.path.join(root, player_file)
                print(f"Found {position} file: {player_file}")
                add_player_to_team_csv(player_file_path, position)

# Check if the folders exist and contain CSV files
print(f"Checking player folders...")
print(f"QB folder exists: {os.path.exists(qb_stats_folder)}")
print(f"RB folder exists: {os.path.exists(rb_stats_folder)}")
print(f"WR folder exists: {os.path.exists(wr_stats_folder)}")
print(f"Kicker folder exists: {os.path.exists(kicker_stats_folder)}")

# Process each folder
process_folder(qb_stats_folder, 'QB', '_career_passing_stats.csv')
process_folder(rb_stats_folder, 'RB', '_career_rushing_stats.csv')
process_folder(wr_stats_folder, 'WR', '_career_receiving_stats.csv')
process_folder(kicker_stats_folder, 'K', '_career_stats.csv')

print("Script finished running.")
