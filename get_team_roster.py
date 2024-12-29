import os
import csv

# Input and output file paths
input_file = 'nfl_roster.csv'  # Updated file name
output_folder = 'teams'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Dictionary to hold data for each team
team_data = {}

# Offensive positions
offensive_positions = {'QB', 'WR', 'RB', 'TE', 'OL'}

# Attempt to handle encoding issues
try:
    with open(input_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Separate first and last name
            full_name = row['Name'].split(', ')
            row['Last Name'] = full_name[0]
            row['First Name'] = full_name[1] if len(full_name) > 1 else ''
            
            # Group by team
            team = row['Team']
            if team not in team_data:
                team_data[team] = {'offense': [], 'defense': []}
            
            # Classify player as offense or defense
            position = row['Pos.']
            if position in offensive_positions:
                team_data[team]['offense'].append(row)
            else:
                team_data[team]['defense'].append(row)
except UnicodeDecodeError:
    with open(input_file, mode='r', newline='', encoding='latin1') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Separate first and last name
            full_name = row['Name'].split(', ')
            row['Last Name'] = full_name[0]
            row['First Name'] = full_name[1] if len(full_name) > 1 else ''
            
            # Group by team
            team = row['Team']
            if team not in team_data:
                team_data[team] = {'offense': [], 'defense': []}
            
            # Classify player as offense or defense
            position = row['Pos.']
            if position in offensive_positions:
                team_data[team]['offense'].append(row)
            else:
                team_data[team]['defense'].append(row)

# Write CSV files for each team, one for offense and one for defense
for team, categories in team_data.items():
    for category, players in categories.items():
        output_file = os.path.join(output_folder, f'{team}_{category}.csv')
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            # Determine fieldnames and include new columns
            fieldnames = ['First Name', 'Last Name', 'Pos.', 'Ht.', 'Wt.']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write players in the category (offense or defense)
            for player in players:
                writer.writerow({
                    'First Name': player['First Name'],
                    'Last Name': player['Last Name'],
                    'Pos.': player['Pos.'],
                    'Ht.': player['Ht.'],
                    'Wt.': player['Wt.']
                })

print(f"Offense and defense CSV files have been created in the '{output_folder}' folder.")
