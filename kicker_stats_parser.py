import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Read the CSV file
df = pd.read_csv('official_kicker_stats.csv')

# Create folders to save the stats if they don't exist
main_folder_name = "kicker_stats"
if not os.path.exists(main_folder_name):
    os.makedirs(main_folder_name)

weekly_folder_name = "kicker_weekly_stats"
if not os.path.exists(main_folder_name + "/" + weekly_folder_name):
    os.makedirs(main_folder_name + "/" + weekly_folder_name)

career_folder_name = "kicker_career_stats"
if not os.path.exists(main_folder_name + "/" + career_folder_name):
    os.makedirs(main_folder_name + "/" + career_folder_name)

# Function to scrape weekly stats for a player
def get_weekly_kicker_stats(player_name):
    # Assuming the URL structure includes the player's name, like 'justin-tucker' for Justin Tucker
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/"
    
    # Send a GET request and parse the response
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table')
    
    try:
        # Extract stats and save to CSV
        df_weekly = pd.read_html(str(table), flavor='lxml')[0]
        df_weekly.to_csv(f"{main_folder_name}/{weekly_folder_name}/{player_name.replace(' ', '_')}_weekly_stats.csv", index=False)
        print(f"Saved {player_name}'s weekly stats.")
    except Exception as e:
        print(f"Error for {player_name}: {e}")

# Function to scrape career kicking stats for a player
def get_career_kicker_stats(player_name):
    # Assuming the URL structure includes the player's name, like 'justin-tucker' for Justin Tucker
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/career"
    
    # Send a GET request and parse the response
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table')
    
    try:
        # Extract stats from the first table and save to CSV
        df_career = pd.read_html(str(table), flavor='lxml')[0]
        df_career.to_csv(f"{main_folder_name}/{career_folder_name}/{player_name.replace(' ', '_')}_career_kicking_stats.csv", index=False)
        print(f"Saved {player_name}'s career kicking stats.")
    except Exception as e:
        print(f"Error for {player_name}: {e}")

# Loop through each player in the CSV
for index, row in df.iterrows():
    player_name = row['Player']
    get_weekly_kicker_stats(player_name)
    get_career_kicker_stats(player_name)
