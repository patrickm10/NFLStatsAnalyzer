"""
NFL Offensive Stats Analyzer
Author: Patrick Mejia & Matthew Fredo
Will Save  updated weekly stats for offensive skill positions
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Function to create folders
def create_folders(main_folder_name, weekly_folder_name):
    folder_path = f"{main_folder_name}/{weekly_folder_name}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

# Generalized function to get and sort weekly stats
def get_weekly_stats(player_name, position_folder, weekly_folder):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/"
    
    try:
        # Send a GET request and parse the response
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')

        # Extract stats and save to CSV
        if table:
            df_weekly = pd.read_html(str(table), flavor='lxml')[0]

            # Ensure sorting by "Week" (descending)
            if 'WK' in df_weekly.columns:
                df_weekly['WK'] = pd.to_numeric(df_weekly['WK'], errors='coerce')  # Convert Week to numeric
                df_weekly = df_weekly.sort_values(by='WK', ascending=False)

            file_path = f"{position_folder}/{weekly_folder}/{player_name.replace(' ', '_')}_weekly_stats.csv"
            df_weekly.to_csv(file_path, index=False)
            print(f"Saved {player_name}'s weekly stats to {file_path}.")
        else:
            print(f"No stats table found for {player_name}.")
    except Exception as e:
        print(f"Error for {player_name}: {e}")

# Main function to process players for a position
def process_position(df, main_folder_name, weekly_folder_name):
    folder_path = create_folders(main_folder_name, weekly_folder_name)
    for _, row in df.iterrows():
        first_name = row['First Name']
        last_name = row['Last Name']
        player_name = first_name + " " + last_name
        get_weekly_stats(player_name, main_folder_name, weekly_folder_name)

# Process each position
process_position(pd.read_csv('official_qb_stats.csv'), "qb_stats", "qb_weekly_stats")
process_position(pd.read_csv('official_rb_stats.csv'), "rb_stats", "rb_weekly_stats")
process_position(pd.read_csv('official_wr_stats.csv'), "wr_stats", "wr_weekly_stats")
#process_position(pd.read_csv('official_kicker_stats.csv'), "kicker_stats", "kicker_weekly_stats")
process_position(pd.read_csv('official_te_stats.csv'), "te_stats", "te_weekly_stats")
