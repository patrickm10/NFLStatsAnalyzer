import requests
from bs4 import BeautifulSoup
import pandas as pd
import os


nfl_teams = [
    "Arizona Cardinals",
    "Atlanta Falcons",
    "Baltimore Ravens",
    "Buffalo Bills",
    "Carolina Panthers",
    "Chicago Bears",
    "Cincinnati Bengals",
    "Cleveland Browns",
    "Dallas Cowboys",
    "Denver Broncos",
    "Detroit Lions",
    "Green Bay Packers",
    "Houston Texans",
    "Indianapolis Colts",
    "Jacksonville Jaguars",
    "Kansas City Chiefs",
    "Las Vegas Raiders",
    "Los Angeles Chargers",
    "Los Angeles Rams",
    "Miami Dolphins",
    "Minnesota Vikings",
    "New England Patriots",
    "New Orleans Saints",
    "New York Giants",
    "New York Jets",
    "Philadelphia Eagles",
    "Pittsburgh Steelers",
    "San Francisco 49ers",
    "Seattle Seahawks",
    "Tampa Bay Buccaneers",
    "Tennessee Titans",
    "Washington Commanders",
]

def get_team_roster(team_name):
    """
    Function to scrape the roster
    Args:
        team_name (str): The name of the team to scrape the roster for.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped roster.
    """
    team_name = team_name.lower().replace(" ", "-")
    url = f"https://www.nfl.com/teams/{team_name}/roster"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    team_name = team_name.replace("-", " ").title()
    df["Team"] = team_name  # Add team_name as Team in the dataframe
    return df

    # for team in nfl_teams:
    #     team_roster = get_team_roster(team)
    #     # team_roster.to_csv(f'{team}_roster.csv', index=False)
    #     team_roster.to_csv('nfl_official_team_roster.csv', index=False)
