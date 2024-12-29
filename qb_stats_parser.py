import requests
import pandas as pd
from bs4 import BeautifulSoup
import os

# Read the CSV file containing QB names
df = pd.read_csv('official_qb_stats.csv')

# Create folders to save the stats if they don't exist
main_folder_name = "qb_stats"
weekly_folder_name = "qb_weekly_stats"
if not os.path.exists(main_folder_name + "/" + weekly_folder_name):
    os.makedirs(main_folder_name + "/" + weekly_folder_name)

career_passing_folder_name = "qb_career_passing_stats"
if not os.path.exists(main_folder_name + "/" + career_passing_folder_name):
    os.makedirs(main_folder_name + "/" + career_passing_folder_name)

career_rushing_folder_name = "qb_career_rushing_stats"
if not os.path.exists(main_folder_name + "/" + career_rushing_folder_name):
    os.makedirs(main_folder_name + "/" + career_rushing_folder_name)

# Function to scrape weekly stats for a player
def get_weekly_qb_stats(player_name):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/"
    
    # Send a GET request and parse as before
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

# Function to scrape career passing stats for a player
def get_career_passing_qb_stats(player_name):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/career"
    
    # Send a GET request and parse as before
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table')
    
    try:
        # Extract passing stats and save to CSV
        df_passing = pd.read_html(str(tables[0]), flavor='lxml')[0]
        df_passing.to_csv(f"{main_folder_name}/{career_passing_folder_name}/{player_name.replace(' ', '_')}_career_passing_stats.csv", index=False)
        print(f"Saved {player_name}'s career passing stats.")
    except Exception as e:
        print(f"Error for {player_name}: {e}")

# Function to scrape career rushing stats for a player
def get_career_rushing_qb_stats(player_name):
    url = f"https://www.nfl.com/players/{player_name.replace(' ', '-').lower()}/stats/career"
    
    # Send a GET request and parse as before
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    tables = soup.find_all('table')
    
    try:
        # Extract rushing stats and save to CSV
        df_rushing = pd.read_html(str(tables[1]), flavor='lxml')[0]
        df_rushing.to_csv(f"{main_folder_name}/{career_rushing_folder_name}/{player_name.replace(' ', '_')}_career_rushing_stats.csv", index=False)
        print(f"Saved {player_name}'s career rushing stats.")
    except Exception as e:
        print(f"Error for {player_name}: {e}")

# Loop through each player in the CSV
for index, row in df.iterrows():
    player_name = row['Player']
    
    # Get weekly stats
    get_weekly_qb_stats(player_name)
    
    # Get career passing stats
    get_career_passing_qb_stats(player_name)
    
    # Get career rushing stats
    get_career_rushing_qb_stats(player_name)
