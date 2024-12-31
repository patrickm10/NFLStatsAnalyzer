import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Read the CSV file
df = pd.read_csv('official_wr_stats.csv')

# Create folders to save the stats if they don't exist
main_folder_name = "wr_stats"
weekly_folder_name = "wr_weekly_stats"
if not os.path.exists(main_folder_name + "/" + weekly_folder_name):
    os.makedirs(main_folder_name + "/" + weekly_folder_name)

receiving_career_folder_name = "wr_career_receiving_stats"
if not os.path.exists(main_folder_name + "/" + receiving_career_folder_name):
    os.makedirs(main_folder_name + "/" + receiving_career_folder_name)

rushing_career_folder_name = "wr_career_rushing_stats"
if not os.path.exists(main_folder_name + "/" + rushing_career_folder_name):
    os.makedirs(main_folder_name + "/" + rushing_career_folder_name)

# Function to scrape weekly stats for a player
def get_weekly_wr_stats(player_name):
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

# Function to scrape career receiving stats for a player
def get_career_receiving_stats(player_name):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/career"
    
    # Send a GET request and parse the response
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table')
    
    try:
        # Extract the first table (receiving stats) and save to CSV
        df_receiving = pd.read_html(str(tables[0]), flavor='lxml')[0]
        df_receiving.to_csv(f"{main_folder_name}/{receiving_career_folder_name}/{player_name.replace(' ', '_')}_career_receiving_stats.csv", index=False)
        print(f"Saved {player_name}'s career receiving stats.")
    except Exception as e:
        print(f"Error for {player_name} (Receiving): {e}")

# Function to scrape career rushing stats for a player
def get_career_rushing_stats(player_name):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/career"
    
    # Send a GET request and parse the response
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table')
    
    try:
        # Extract the second table (rushing stats) and save to CSV
        df_rushing = pd.read_html(str(tables[1]), flavor='lxml')[0]
        df_rushing.to_csv(f"{main_folder_name}/{rushing_career_folder_name}/{player_name.replace(' ', '_')}_career_rushing_stats.csv", index=False)
        print(f"Saved {player_name}'s career rushing stats.")
    except Exception as e:
        print(f"Error for {player_name} (Rushing): {e}")

# Loop through each player in the CSV
for index, row in df.iterrows():
    player_name = row['Player']
    get_weekly_wr_stats(player_name)
    get_career_receiving_stats(player_name)
    get_career_rushing_stats(player_name)
