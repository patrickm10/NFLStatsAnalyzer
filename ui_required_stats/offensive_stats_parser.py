"""
NFL Offensive Stats Analyzer
Author: Patrick Mejia
"""
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd
import os
import csv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAI
import logging


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

def get_team_td_stats():
    """
    Function to scrape kicking stats from the NFL website.
    Returns: df (DataFrame): A pandas DataFrame containing the scraped kicking stats.
    """
    url = "https://www.nfl.com/stats/team-stats/offense/scoring/2024/reg/all"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    return df

def find_best_team_td(df):
    """
    Function to find the best kicker based on a kicker score that incorporates field goal percentage,
    distance ranges, and field goal attempts as a percentage of the top kicker's attempts.
    Args:
        df (DataFrame): A pandas DataFrame containing the kicking stats.
    Returns:
        best_kickers (DataFrame): A pandas DataFrame containing the top kickers ranked by their kicker score.
    """

    # Initialize the weighted score column and ensure FG and Att are integers
    df["Weighted Score"] = 0
    # print(df.columns)
    df["Team"] = df["Team"].str.split().str[0]
    df["Rsh TD"] = df["Rsh TD"].astype(int)
    df["Rec TD"] = df["Rec TD"].astype(int)
    df["Tot TD"] = df["Tot TD"].astype(int)
    df["2-PT"] = df["2-PT"].astype(int)

    df["Score"] = (
        (df["Rsh TD"] * 0.25)
        + (df["Rec TD"] * 0.25)
        + (df["Tot TD"] * 0.4)
        + (df["2-PT"] * 0.1)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort quarterbacks by the composite score in descending order
    best_team_td = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(25)

    # Print the top quarterbacks
    # print(best_team_td)

    # Optionally, save the top quarterbacks to a new CSV file
    best_team_td.to_csv("official_team_td_stats.csv", index=False)

    return best_team_td

def get_schedule(csv_file):
    """
    Function to parse team stats from a CSV file and compute scores based on match results.
    Args:
        csv_file (str): Path to the CSV file containing match data.
    Returns:
        df (DataFrame): A pandas DataFrame containing the computed team stats.
    """
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Extract home and away teams and their respective scores from the 'Result' column
    df[["Home Score", "Away Score"]] = df["Result"].str.split(" - ", expand=True)
    df["Home Score"] = pd.to_numeric(df["Home Score"], errors="coerce")
    df["Away Score"] = pd.to_numeric(df["Away Score"], errors="coerce")

    # Initialize the team statistics dictionary
    team_stats = {}

    # Loop through each match and update the stats for home and away teams
    for _, row in df.iterrows():
        home_team = row["Home Team"]
        away_team = row["Away Team"]
        home_score = row["Home Score"]
        away_score = row["Away Score"]

        # Update home team stats
        if home_team not in team_stats:
            team_stats[home_team] = {
                "Wins": 0,
                "Losses": 0,
                "Total Points": 0,
                "Games Played": 0,
            }
        team_stats[home_team]["Games Played"] += 1
        team_stats[home_team]["Total Points"] += home_score
        if home_score > away_score:
            team_stats[home_team]["Wins"] += 1
        else:
            team_stats[home_team]["Losses"] += 1

        # Update away team stats
        if away_team not in team_stats:
            team_stats[away_team] = {
                "Wins": 0,
                "Losses": 0,
                "Total Points": 0,
                "Games Played": 0,
            }
        team_stats[away_team]["Games Played"] += 1
        team_stats[away_team]["Total Points"] += away_score
        if away_score > home_score:
            team_stats[away_team]["Wins"] += 1
        else:
            team_stats[away_team]["Losses"] += 1

    # Convert the stats into a DataFrame
    stats_data = []
    for team, stats in team_stats.items():
        stats_data.append(
            [
                team,
                stats["Games Played"],
                stats["Wins"],
                stats["Losses"],
                stats["Total Points"],
            ]
        )

    stats_df = pd.DataFrame(
        stats_data, columns=["Team", "Games Played", "Wins", "Losses", "Total Points"]
    )

    # Calculate a weighted score for each team (this is a basic example, feel free to adjust the weights)
    stats_df["Score"] = (
        (stats_df["Wins"] * 0.5)
        + (stats_df["Total Points"] * 0.3)
        - (stats_df["Losses"] * 0.2)
    )

    # Normalize the score (0 to 100 scale)
    stats_df["Normalized Score"] = (
        (stats_df["Score"] - stats_df["Score"].min())
        / (stats_df["Score"].max() - stats_df["Score"].min())
        * 100
    )

    # Sort teams by the normalized score in descending order
    best_teams = stats_df.sort_values(
        by="Normalized Score", ascending=False, ignore_index=True
    )

    # Optionally, save the top teams to a CSV file
    best_teams.to_csv("best_team_td_stats.csv", index=False)

    return best_teams

def get_nfl_records():
    """
    Function to scrape NFL team records from the NFL website.
    Returns: df (DataFrame): A pandas DataFrame containing the scraped NFL team records.
    """
    url = "https://www.nfl.com/standings/league/2024/REG"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    team_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        team = [td.get_text().strip() for td in row.find_all("td")]
        team_data.append(team)
    df = pd.DataFrame(team_data, columns=headers)
    return df

def add_divisions_to_teams(df, df2):
    """
    Function to add divisions to the team stats DataFrame.
    Args:
        df (DataFrame): A pandas DataFrame containing the team stats.
        df2 (DataFrame): A pandas DataFrame containing the team divisions.
    Returns:
        df (DataFrame): A pandas DataFrame containing the team stats with divisions.
    """
    # Merge the two DataFrames on the 'NFL Team' column
    df = df.merge(df2, on="Team", how="left")
    df.to_csv("nfl_official_team_roster.csv", index=False)
    return df

def separate_names(df):
    """
    Function to separate the first and last names in a DataFrame column.
    Args:
        df (DataFrame): A pandas DataFrame containing the player names.
    Returns:
        df (DataFrame): A pandas DataFrame with separate columns for first and last names.
    """
    # Split the 'Name' column into 'First Name' and 'Last Name'
    df[["First Name", "Last Name"]] = df["Name"].str.split(" ", 1, expand=True)
    df["First Name"] = df["First Name"].str.strip().str.replace(",", "")
    return df

def reorganize_columns(df):

    """
    Function to reorganize the columns in a DataFrame.
    Args:
        df (DataFrame): A pandas DataFrame to reorganize.
        Returns:
        df (DataFrame): The reorganized DataFrame.
    """
    # Reorganize the columns as needed
    # Ensure the columns exist before reorganizing
    required_columns = [
        "Team",
        "First Name",
        "Last Name",
        "Pos.",
        "Ht.",
        "Wt.",
        "ID",
        "Conference",
        "Division",
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None  # Add missing columns with None values

    df = df[required_columns]
    return df

def read_folder(folder_path):
    """
    Function to read all CSV files in a folder and combine them into a single DataFrame.
    Args:
        folder_path (str): Path to the folder containing the CSV files.
    Returns:
        combined_df (DataFrame): A pandas DataFrame containing the combined data from all CSV files.
    """
    all_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith(".csv")
    ]
    df_list = [pd.read_csv(file) for file in all_files]
    combined_df = pd.concat(df_list, ignore_index=True)
    return combined_df

def organize_rushing_stats():
    """
    Function to combine rushing stats for quarterbacks, running backs, and wide receivers.
    """

    qb_rushing_stats = read_folder("data/qb_stats/qb_career_rushing_stats")
    rb_rushing_stats = read_folder("data/rb_stats/rb_career_rushing_stats")
    wr_rushing_stats = read_folder("data/wr_stats/wr_career_rushing_stats")

    # Combine the rushing stats for all positions
    all_rushing_stats = pd.concat(
        [qb_rushing_stats, rb_rushing_stats, wr_rushing_stats], ignore_index=True
    )
    print(all_rushing_stats)

    # Save the combined rushing stats to a new CSV file
    all_rushing_stats.to_csv("all_career_rushing_stats.csv", index=False)

def organize_receiving_stats():
    """
    Function to combine receiving stats for wide receivers and tight ends.
    """
    wr_receiving_stats = pd.read_csv("data/wr_career_receiving_stats.csv")
    rb_receiving_stats = pd.read_csv("data/rb_career_receiving_stats.csv")

    # Combine the receiving stats for wide receivers and tight ends
    top_receiving_stats = pd.concat(
        [wr_receiving_stats, rb_receiving_stats], ignore_index=True
    )
    print(top_receiving_stats)

    # Save the combined receiving stats to a new CSV file
    top_receiving_stats.to_csv("top_receiving_stats.csv", index=False)

def find_best_teams(df):
    """
    Function to find the best teams based on wins, losses, and points scored.
    Args:
        df (DataFrame): A pandas DataFrame containing the team stats.
        Returns:
        best_teams (DataFrame): A pandas DataFrame containing the top teams ranked by a composite score.
    """
    # Convert relevant columns to numeric values
    df["NFL Team"] = df["NFL Team"].str.split().str[:3].str.join(" ")
    df["W"] = pd.to_numeric(df["W"], errors="coerce").fillna(0).astype(int)
    df["L"] = pd.to_numeric(df["L"], errors="coerce").fillna(0).astype(int)
    df["PF"] = pd.to_numeric(df["PF"], errors="coerce").fillna(0).astype(int)
    df["PA"] = pd.to_numeric(df["PA"], errors="coerce").fillna(0).astype(int)
    df["Net Pts"] = pd.to_numeric(df["Net Pts"], errors="coerce").fillna(0).astype(int)
    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["W"] * 0.5)
        + (df["PF"] * 0.3)
        + (df["Net Pts"] * 0.2)
        - (df["PA"] * 0.1)
        - (df["L"] * 0.2)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort teams by the composite score in descending order
    best_teams = df.sort_values(by="Weighted Score", ascending=False).head(32)

    # Print the top teams
    # print(best_teams)

    # Optionally, save the top teams to a new CSV file
    best_teams.to_csv("nfl_official_team_stats.csv", index=False)

    return best_teams

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

def find_best_kickers():
    """
    Function to find the best kicker based on a kicker score that incorporates field goal percentage,
    distance ranges, and field goal attempts as a percentage of the top kicker's attempts.
    Args:
        df (DataFrame): A pandas DataFrame containing the kicking stats.
    Returns:
        best_kickers (DataFrame): A pandas DataFrame containing the top kickers ranked by their kicker score.
    """
    url = "https://www.fantasypros.com/nfl/stats/k.php?scoring=PPR"
    
    try:
        # Fetch the page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None
        
        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]
        
        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):
                player_data.append(player)
                
        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None
        
        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        # print(df.columns)
        # print(df.head(50))
        
        # Check if there are duplicate "FG" columns and drop the second one
        if df.columns.tolist().count("FG") > 1:
            # print("Duplicate 'FG' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]
            
        # print("Cleaned DataFrame columns:", df.columns)
        
        # Convert relevant columns to numeric
        df["FG"] = pd.to_numeric(df["FG"], errors="coerce").fillna(0).astype(int)
        df["FGA"] = pd.to_numeric(df["FGA"], errors="coerce").fillna(0).astype(int)
        df["PCT"] = pd.to_numeric(df["PCT"], errors="coerce").fillna(0).astype(float)
        df["1-19"] = pd.to_numeric(df["1-19"], errors="coerce").fillna(0).astype(int)
        df["20-29"] = pd.to_numeric(df["20-29"], errors="coerce").fillna(0).astype(int)
        df["30-39"] = pd.to_numeric(df["30-39"], errors="coerce").fillna(0).astype(int)
        df["40-49"] = pd.to_numeric(df["40-49"], errors="coerce").fillna(0).astype(int)
        df["50+"] = pd.to_numeric(df["50+"], errors="coerce").fillna(0).astype(int)
        df["FPTS/G"] = pd.to_numeric(df["FPTS/G"], errors="coerce").fillna(0).astype(float)
        df["FPTS"] = pd.to_numeric(df["FPTS"], errors="coerce").fillna(0).astype(float)
        
        # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
        df["Score"] = (
            (df["FG"] * 0.5)
            + (df["FGA"] * 0.3)
            + (df["PCT"] * 0.2)
            + (df["1-19"] * 0.1)
            + (df["20-29"] * 0.1)
            + (df["30-39"] * 0.1)
            + (df["40-49"] * 0.1)
            + (df["50+"] * 0.1)
            + (df["FPTS/G"] * 0.3)
            + (df["FPTS"] * 0.2)
        )
        
        # Sort kickers by the composite score in descending order
        best_kickers = df.sort_values(by="Score", ascending=False, ignore_index=True).head(32)
        
        df["Score"] = df["Score"].astype(float)
        df["Weighted Score"] = (
            (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
        ) * 100
        
        df["Weighted Score"] = df["Weighted Score"].astype(float)
        
        # Print the top kickers
        # print(best_kickers)
        
        # Save to CSV
        best_kickers.to_csv("official_kicker_stats.csv", index=False)
        print("Top kicker stats saved to 'official_kicker_stats.csv'.")
        
        return best_kickers
    
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return None

def find_best_qbs():
    """
    Function to find the best quarterbacks based on passing yards, touchdowns, yards per attempt, and completion percentage.
    Args:
        df (DataFrame): A pandas DataFrame containing the passing stats.
    Returns:
        best_qbs (DataFrame): A pandas DataFrame containing the top quarterbacks ranked by a composite score.
    """
    # Convert passing yards and touchdowns to numeric values
    # Convert relevant columns to numeric values
    url = "https://www.fantasypros.com/nfl/stats/qb.php?scoring=PPR"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None

        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]
        
        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):
                player_data.append(player)

        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None

        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        # print(df.head(50))

        # Check if there are duplicate "YDS" columns and drop the second one
        if df.columns.tolist().count("YDS") > 1:
            # print("Duplicate 'YDS' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]

        # print("Cleaned DataFrame columns:", df.columns)

        # Remove commas from YDS column (ensure we're working with the correct one)
        df["YDS"] = df["YDS"].str.replace(",", "", regex=True)

        # Convert relevant columns to numeric
        df["CMP"] = pd.to_numeric(df["CMP"], errors="coerce").fillna(0).astype(int)
        df["YDS"] = pd.to_numeric(df["YDS"], errors="coerce").fillna(0).astype(int)
        df["TD"] = pd.to_numeric(df["TD"], errors="coerce").fillna(0).astype(int)
        df["Y/A"] = pd.to_numeric(df["Y/A"], errors="coerce").fillna(0).astype(float)
        df["INT"] = pd.to_numeric(df["INT"], errors="coerce").fillna(0).astype(int)
        df["FPTS/G"] = pd.to_numeric(df["FPTS/G"], errors="coerce").fillna(0).astype(float)
        df["FPTS"] = pd.to_numeric(df["FPTS"], errors="coerce").fillna(0).astype(float)

        # Calculate composite score
        df["Score"] = (df["YDS"] * 0.45) + (df["TD"] * 0.4) + (df["Y/A"] * 0.15) - (df["INT"] * 0.2) + (df["FPTS/G"] * 0.3) + (df["FPTS"] * 0.2)
        + (df["CMP"] * 0.1)

        # Sort and select top players
        best_qbs = df.sort_values(by="Score", ascending=False, ignore_index=True).head(32)

        # Save to CSV
        best_qbs.to_csv("official_qb_stats.csv", index=False)
        print("Top QB stats saved to 'official_qb_stats.csv'.")

        return best_qbs
    
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def find_best_rbs():    
    """
    Function to find the best running backs based on rushing yards, touchdowns, yards per carry, and fumbles.
    Args:
        df (DataFrame): A pandas DataFrame containing the rushing stats.
        Returns:
        best_rbs (DataFrame): A pandas DataFrame containing the top running backs ranked by a composite score.
    """
    url = "https://www.fantasypros.com/nfl/stats/rb.php?scoring=PPR"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None

        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]

        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):
                player_data.append(player)
                
        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None

        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        # print(df.columns)
        # print(df.head(50))

        # Check if there are duplicate "YDS" columns and drop the second one
        if df.columns.tolist().count("YDS") > 1:
            # print("Duplicate 'YDS' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]

        # print("Cleaned DataFrame columns:", df.columns)

        # Remove commas from YDS column (ensure we're working with the correct one)
        df["YDS"] = df["YDS"].str.replace(",", "", regex=True)

        # Convert relevant columns to numeric
        df["ATT"] = pd.to_numeric(df["ATT"], errors="coerce").fillna(0).astype(int)
        df["YDS"] = pd.to_numeric(df["YDS"], errors="coerce").fillna(0).astype(int)
        df["TD"] = pd.to_numeric(df["TD"], errors="coerce").fillna(0).astype(int)
        df["Y/A"] = pd.to_numeric(df["Y/A"], errors="coerce").fillna(0).astype(float)
        df["FPTS/G"] = pd.to_numeric(df["FPTS/G"], errors="coerce").fillna(0).astype(float)
        df["FPTS"] = pd.to_numeric(df["FPTS"], errors="coerce").fillna(0).astype(float)
        df["FL"] = pd.to_numeric(df["FL"], errors="coerce").fillna(0).astype(int)
        df["REC"] = pd.to_numeric(df["REC"], errors="coerce").fillna(0).astype(int)
        # Calculate composite score
        df["Score"] = (df["YDS"] * 0.45) + (df["TD"] * 0.4) + (df["Y/A"] * 0.15) + (df["FPTS/G"] * 0.3) + (df["FPTS"] * 0.2)
        + (df["ATT"] * 0.1)
        - (df["FL"] * 0.1)
        + (df["REC"] * 0.1)

        # Sort and select top players
        best_rbs = df.sort_values(by="Score", ascending=False, ignore_index=True).head(32)

        # Save to CSV
        best_rbs.to_csv("official_rb_stats.csv", index=False)
        print("Top RB stats saved to 'official_rb_stats.csv'.")

        return best_rbs

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

def find_best_tes():
    """
    Function to find the best tight ends based on receiving stats.

    Returns:
        best_tes (DataFrame): A pandas DataFrame containing the top tight ends ranked by a composite score.
    """
    url = "https://www.fantasypros.com/nfl/stats/te.php"

    try:
        # Fetch the page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None

        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]

        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):  # Ensure row matches header count
                player_data.append(player)

        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None

        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        # print(df.head(50))

        # Check if there are duplicate "YDS" columns and drop the second one
        if df.columns.tolist().count("YDS") > 1:
            # print("Duplicate 'YDS' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]  # Keep only the first occurrence of each column

        # print("Cleaned DataFrame columns:", df.columns)

        # Remove commas from YDS column (ensure we're working with the correct one)
        df["YDS"] = df["YDS"].str.replace(",", "", regex=True)

        # Convert relevant columns to numeric
        df["REC"] = pd.to_numeric(df["REC"], errors="coerce").fillna(0).astype(int)
        df["YDS"] = pd.to_numeric(df["YDS"], errors="coerce").fillna(0).astype(int)
        df["TD"] = pd.to_numeric(df["TD"], errors="coerce").fillna(0).astype(int)
        df["Y/R"] = pd.to_numeric(df["Y/R"], errors="coerce").fillna(0).astype(float)
        df["LG"] = pd.to_numeric(df["LG"], errors="coerce").fillna(0).astype(int)
        df["20+"] = pd.to_numeric(df["20+"], errors="coerce").fillna(0).astype(int)
        df["FPTS/G"] = pd.to_numeric(df["FPTS/G"], errors="coerce").fillna(0).astype(float)
        df["FPTS"] = pd.to_numeric(df["FPTS"], errors="coerce").fillna(0).astype(float)

        # Calculate composite score
        df["Score"] = (df["REC"] * 0.35) + (df["YDS"] * 0.25) + (df["TD"] * 0.5)

        # Sort and select top players
        best_tes = df.sort_values(by="Score", ascending=False, ignore_index=True).head(50)

        # Save to CSV
        best_tes.to_csv("official_te_stats.csv", index=False)
        print("Top TE stats saved to 'official_te_stats.csv'.")

        return best_tes

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

def find_best_wrs():
    """
    Function to find the best wide receivers based on receiving yards, receptions, yards per reception, and touchdowns.
    Args:
        df (DataFrame): A pandas DataFrame containing the receiving stats.
    Returns:
        best_wrs (DataFrame): A pandas DataFrame containing the top wide receivers ranked by a composite score.
    """
    url = "https://www.fantasypros.com/nfl/stats/wr.php?scoring=PPR"
    try:
        # Fetch the page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None
        
        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]
        
        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):
                player_data.append(player)
                
        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None
        
        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        # print(df.head(50))
        
        # Check if there are duplicate "YDS" columns and drop the second one
        if df.columns.tolist().count("YDS") > 1:
            # print("Duplicate 'YDS' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]
            
        # print("Cleaned DataFrame columns:", df.columns)
        
        # Remove commas from YDS column (ensure we're working with the correct one)
        df["YDS"] = df["YDS"].str.replace(",", "", regex=True)
        
        # Convert relevant columns to numeric
        df["REC"] = pd.to_numeric(df["REC"], errors="coerce").fillna(0).astype(int)
        df["YDS"] = pd.to_numeric(df["YDS"], errors="coerce").fillna(0).astype(int)
        df["TD"] = pd.to_numeric(df["TD"], errors="coerce").fillna(0).astype(int)
        df["Y/R"] = pd.to_numeric(df["Y/R"], errors="coerce").fillna(0).astype(float)
        df["LG"] = pd.to_numeric(df["LG"], errors="coerce").fillna(0).astype(int)
        df["20+"] = pd.to_numeric(df["20+"], errors="coerce").fillna(0).astype(int)
        
        # Calculate composite score
        df["Score"] = (df["REC"] * 0.35) + (df["YDS"] * 0.25) + (df["TD"] * 0.5)
        + (df["Y/R"] * 0.15)
        + (df["LG"] * 0.1)
        + (df["20+"] * 0.1)
        
        # Sort and select top players
        best_wrs = df.sort_values(by="Score", ascending=False, ignore_index=True).head(50)
        
        # Save to CSV
        best_wrs.to_csv("official_wr_stats.csv", index=False)
        print("Top WR stats saved to 'official_wr_stats.csv'.")
        
        return best_wrs
    
    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return None

def find_top_players(position):
    """
    Function to find the top players based on a given position.
    Args:
        position (str): The position to find the top players for.
        Returns:
        best_players (DataFrame): A pandas DataFrame containing the top players for the given position.
        """
    url = f"https://www.fantasypros.com/nfl/stats/{position}.php"

    try:
        # Fetch the page content
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", {"class": "table"})
        if not table:
            print("Table not found on the page.")
            return None

        # Extract headers and rows
        headers = [th.get_text().strip() for th in table.find("thead").find_all("th")]

        player_data = []
        for row in table.find("tbody").find_all("tr"):
            player = [td.get_text().strip() for td in row.find_all("td")]
            if len(player) == len(headers):  # Ensure row matches header count
                player_data.append(player)

        # Create DataFrame only if player_data is not empty
        if not player_data:
            print("No player data found.")
            return None

        df = pd.DataFrame(player_data, columns=headers)
        df.columns = df.columns.str.strip()  # Clean column names
        print(df.head(50))

        # Check if there are duplicate "YDS" columns and drop the second one
        if df.columns.tolist().count("YDS") > 1:
            # print("Duplicate 'YDS' columns found. Keeping the first one.")
            df = df.loc[:, ~df.columns.duplicated()]

        # print("Cleaned DataFrame columns:", df.columns)

        # Remove commas from YDS column (ensure we're working with the correct one)
        df["YDS"] = df["YDS"].str.replace(",", "", regex=True)

        # Convert relevant columns to numeric
        df["REC"] = pd.to_numeric(df["REC"], errors="coerce").fillna(0).astype(int)
        df["YDS"] = pd.to_numeric(df["YDS"], errors="coerce").fillna(0).astype(int)
        df["TD"] = pd.to_numeric(df["TD"], errors="coerce").fillna(0).astype(int)
        df["Y/R"] = pd.to_numeric(df["Y/R"], errors="coerce").fillna(0).astype(float)
        df["LG"] = pd.to_numeric(df["LG"], errors="coerce").fillna(0).astype(int)
        df["20+"] = pd.to_numeric
        df["FPTS/G"] = pd.to_numeric(df["FPTS/G"], errors="coerce").fillna(0).astype(float)
        df["FPTS"] = pd.to_numeric(df["FPTS"], errors="coerce").fillna(0).astype(float)

        # Calculate composite score
        if position == "QB":
            df["Score"] = (df["YDS"] * 0.45) + (df["TD"] * 0.4) + (df["YDS/ATT"] * 0.15)
        elif position == "RB":
            df["Score"] = (df["REC"] * 0.35) + (df["YDS"] * 0.25) + (df["TD"] * 0.5)
        elif position == "WR":
            df["Score"] = (df["REC"] * 0.35) + (df["YDS"] * 0.25) + (df["TD"] * 0.5)
        elif position == "TE":
            df["Score"] = (df["REC"] * 0.35) + (df["YDS"] * 0.25) + (df["TD"] * 0.5)
        elif position == "K":
            df["Score"] = (df["FG"] * 0.5) + (df["Att"] * 0.3) + (df["PCT"] * 0.2)
        else:
            print("Invalid position specified.")
            return None


        df["Normalized_Score"] = (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min()) * 100
        # Sort and select top players
        best_players = df.sort_values(by="Score", ascending=False, ignore_index=True).head(50)

        # Save to CSV
        best_players.to_csv(f"official_{position}_stats.csv", index=False)

        return best_players

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

# TODO: Change function to use schedule vs defense stats
def find_best_wr_defense_matchups(df1, df2):
    """
    Function to find the best wide receiver versus defense matchups based on a combination of receiving and defense stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the receiving stats.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats.
        Returns:
        best_matchups (DataFrame): A pandas DataFrame containing the top matchups ranked by a composite score.
    """
    # Normalize the scores for each category
    df1["Weighted Score"] = (
        (df1["Weighted Score"] - df1["Weighted Score"].min())
        / (df1["Weighted Score"].max() - df1["Weighted Score"].min())
    ) * 100
    df2["Weighted Score"] = (
        (df2["Weighted Score"] - df2["Weighted Score"].min())
        / (df2["Weighted Score"].max() - df2["Weighted Score"].min())
    ) * 100

    # Combine the scores for receiving and defense
    df1["Combined Score"] = df1["Weighted Score"] + df2["Weighted Score"]

    # Sort matchups by the combined score in descending order
    best_matchups = df1.sort_values(by="Combined Score", ascending=True).head(32)

    # Print the top matchups
    # print(best_matchups)

    # Optionally, save the top matchups to a new CSV file
    best_matchups.to_csv("official_matchup_stats.csv", index=False)

    return best_matchups

# TODO: Change function to use schedule vs defense stats
def find_best_rb_defense_matchups(df1, df2):
    """
    Function to find the best wide receiver versus defense matchups based on a combination of receiving and defense stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the receiving stats.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats.
        Returns:
        best_matchups (DataFrame): A pandas DataFrame containing the top matchups ranked by a composite score.
    """
    # Normalize the scores for each category
    df1["Weighted Score"] = (
        (df1["Weighted Score"] - df1["Weighted Score"].min())
        / (df1["Weighted Score"].max() - df1["Weighted Score"].min())
    ) * 100
    df2["Weighted Score"] = (
        (df2["Weighted Score"] - df2["Weighted Score"].min())
        / (df2["Weighted Score"].max() - df2["Weighted Score"].min())
    ) * 100

    # Combine the scores for receiving and defense
    df1["Combined Score"] = df1["Weighted Score"] + df2["Weighted Score"]

    # Sort matchups by the combined score in descending order
    best_matchups = df1.sort_values(by="Combined Score", ascending=True).head(32)

    # Print the top matchups
    # print(best_matchups)

    # Optionally, save the top matchups to a new CSV file
    best_matchups.to_csv("official_matchup_stats.csv", index=False)

    return best_matchups

def get_offensive_stats():
    """
    Function to combine all offensive stats for quarterbacks, running backs, wide receivers, and tight ends.
    """

    # top_kickers = find_best_kickers(kicking_df)
    # top_qbs = find_best_qbs(passing_df)
    # top_rbs = find_best_rbs(rushing_df)
    # top_wrs = find_best_wrs(receiving_df)
    # top_tes = find_best_tes(te_df)

    # print(top_kickers)
    # print(top_qbs)
    # print(top_rbs)
    # print(top_wrs)
    # print(top_tes)

def remove_team_from_player_name(df):
    """
    Function to remove the team name from the player name.
    Args:
        player_name (str): The player name.
        team_name (str): The team name.
    Returns:
        player_name (str): The player name without the team name.
    """
    df["Player"] = df["Player"].str.replace(r"\(.*?\)", "", regex=True).str.strip()
    return df

# Set up logging for better error tracking and debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Loads api key
load_dotenv()
open_api_key = os.getenv("OPENAI_API_KEY")

# # Check for the API key and raise an error if missing
# if not open_api_key:
#     logger.error("API key not found in the environment. Please set OPENAI_API_KEY.")
#     raise ValueError("API key not found in the environment. Please set OPENAI_API_KEY.")
# else:
#     logger.info("API key successfully loaded.")

# # Function to initialize OpenAI LLM
# def initialize_llm(api_key: str):
#     try:
#         llm = OpenAI(api_key=api_key, temperature=0)
#         logger.info("Successfully connected to OpenAI API.")
#         return llm
#     except Exception as e:
#         logger.error(f"Error connecting to OpenAI API: {e}")
#         raise

# # Initialize OpenAI LLM
# llm = initialize_llm(open_api_key)

# Function to generate AI-powered NFL insights from CSV
def analyze_nfl_stats(question: str, csv_data: str) -> str:
    """Uses an LLM to analyze NFL stats based on a CSV dataset.
    
    Args:
        question (str): The question to analyze.
        csv_data (str): A string representation of the CSV data to be analyzed.

    Returns:
        str: The LLM-generated response based on the data and question.
    """
    prompt = PromptTemplate(
        input_variables=["question", "data"],
        template="""
        Based on the NFL statistics provided below, answer the question:
        {question}

        Data:
        {data}

        Provide a structured response.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    try:
        response = chain.run({"question": question, "data": csv_data})
        return response
    except Exception as e:
        logger.error(f"Error generating insights from LLM: {e}")
        return f"Error generating insights: {e}"

# Function to filter and process NFL stats based on the question
def query_nfl_stats(question: str, df: pd.DataFrame) -> str:
    """Filters the dataset using Pandas before passing it to LangChain.

    Args:
        question (str): The question to analyze.
        df (pd.DataFrame): The DataFrame containing the NFL stats.

    Returns:
        str: The LLM-generated response.
    """
    # Check if question contains a reference to yards (YDS)
    if "YDS" in question.upper():
        logger.info("Filtering the dataset to find the top player based on YDS...")
        top_player = df[df["YDS"] == df["YDS"].max()]
        return analyze_nfl_stats(f"Summarize the performance of {top_player.iloc[0]['Player']}.", df.to_string(index=False))

    # If not related to YDS, fallback to processing full dataset
    return analyze_nfl_stats(question, df.to_string(index=False))

# Function to create a player profile based on stats
def create_player_profile(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Creates a player profile based on the player's stats.

    Args:
        df (pd.DataFrame): DataFrame containing the player stats.
        player_name (str): Name of the player to create a profile for.

    Returns:
        pd.DataFrame: DataFrame with the player profile.
    """
    player_profile = df[df["Player"] == player_name]

    if player_profile.empty:
        logger.error(f"Player '{player_name}' not found in the dataset.")
        return pd.DataFrame()  # Return empty DataFrame if player not found

    # Create LLM input string for profile generation
    llm_input = f"Create a player profile for {player_name} based on the following stats:\n"
    llm_input += player_profile.to_string(index=False)

    try:
        player_profile["Profile"] = analyze_nfl_stats(llm_input, player_profile.to_string(index=False))
        logger.info(f"Player Profile for {player_name} created successfully.")
    except Exception as e:
        logger.error(f"Error generating profile for player '{player_name}': {e}")

    # Display and return the player profile
    logger.info(f"Generated Player Profile for {player_name}:")
    logger.info(player_profile["Profile"].values[0])
    return player_profile

if __name__ == "__main__":
    """
    Main function to scrape and analyze NFL player and team stats.
    """
    print("\n")
    print("NFL Stats Analysis")
    print("*****************")
    print("\n")

    # Scraping Kicking stats
    # print("Scraping kicking stats...")
    top_kickers = find_best_kickers()
    remove_team_from_player_name(top_kickers)
    print(top_kickers)  # Print the top kickers
    # print("\n") 
    # # print("Scraping passing stats...")
    top_qbs = find_best_qbs()
    remove_team_from_player_name(top_qbs)
    print(top_qbs)  # Print the top quarterbacks
    # print("\n")

    # # print("Scraping rushing stats...")
    top_rbs = find_best_rbs()
    remove_team_from_player_name(top_rbs)
    print(top_rbs)  # Print the top running backs
    # print("\n")

    top_tes = find_best_tes()
    remove_team_from_player_name(top_tes)
    print(top_tes)  # Print the top tight ends
    # print("\n")

    # # print("Scraping receiving stats...")
    top_wrs = find_best_wrs()
    remove_team_from_player_name(top_wrs)
    print(top_wrs)  # Print the top wide receivers
    # print("\n")

    # Testing Lanchain with a sample question
    # try:
    #     # Load NFL stats CSV
    #     nfl_stats_df = pd.read_csv("official_qb_stats.csv")

    #     # Query stats (example)
    #     question = "Who had the most passing yards in the 2023 season?"
    #     result = query_nfl_stats(question, nfl_stats_df)
    #     logger.info(result)

    #     # Create player profile (example)
    #     player_name = "Josh Allen"
    #     player_profile = create_player_profile(nfl_stats_df, player_name)

    #     # Print the player profile
    #     print(player_profile)
    
    # # exception handling
    # except Exception as e:
    #     logger.error(f"An error occurred during execution: {e}")

    # print("Scraping Team TD stats...")
    # team_td_df = get_team_td_stats()
    # top_team_td = find_best_team_td(team_td_df)
    # print(top_team_td)  # Print the top wide receivers
    # print("\n")

    # csv_file = "schedule.csv"

    # Get scores for week 1-18
    # for week in range(1, 18):
    #     nfl_scores = []
    #     nfl_scores = get_nfl_scores(week)
    #     print(nfl_scores)
    #     nfl_scores.to_csv('nfl_official_scores.csv', index=False)
    # nfl_week1 = get_nfl_scores(1)
    # print(nfl_week1)

    # Find the best wide receiver versus defense matchups
    # best_matchups = find_best_wr_defense_matchups(top_wrs, top_defenses_receiving)
    # print("Best Wide Receiver vs. Defense Matchups:")
    # print(best_matchups)  # Print the top matchups
    # print("\n")

    # Find the best running back versus defense matchups
    # best_rb_matchups = find_best_rb_defense_matchups(top_rbs, top_defenses_rushing)
    # print("Best Running Back vs. Defense Matchups:")
    # print(best_rb_matchups)  # Print the top matchups
    # print("\n")
