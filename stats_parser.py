import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_stats(url):
    """
    Function to scrape player stats from a given NFL URL.
    
    Args:
        url (str): The URL of the NFL stats page to scrape.
        
    Returns:
        DataFrame: A pandas DataFrame containing the scraped stats.
    """
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}")
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the table containing the player stats
    table = soup.find("table", class_="d3-o-table")
    if not table:
        print(f"No table found on {url}")
        return None

    # Extract column headers
    headers = [th.get_text().strip() for th in table.find_all("th")]

    # Extract player data
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)

    # Create a DataFrame from the scraped data
    df = pd.DataFrame(player_data, columns=headers)
    
    return df

def get_kicking_stats():
    """
    Function to scrape kicking stats from the NFL website.
    Returns: df (DataFrame): A pandas DataFrame containing the scraped kicking stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/field-goals/2024/reg/all/kickingfgmade/desc"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    return df

def find_best_kickers(df):
    """
    Function to find the best kicker based on a kicker score that incorporates field goal percentage,
    distance ranges, and field goal attempts as a percentage of the top kicker's attempts.
    Args:
        df (DataFrame): A pandas DataFrame containing the kicking stats.
    Returns:
        bestKickers (DataFrame): A pandas DataFrame containing the top kickers ranked by their kicker score.
    """
    # List of distance ranges with corresponding weights
    distance_ranges = {
        "20-29": 3.0,
        "30-39": 2.0,
        "40-49": 1.0,
        "50-59": 0.5,
        "60+": 0.25,
    }

    # Initialize the weighted score column and ensure FGM and Att are integers
    df['Weighted Score'] = 0
    df['FGM'] = df['FGM'].astype(int)
    df['Att'] = df['Att'].astype(int)

    # Iterate through the distance ranges and calculate weighted scores
    for distance, weight in distance_ranges.items():
        made_col = f"{distance} > A-M"
        att_col = f"{distance} > A-M"

        # Split made/attempted values into separate columns for made and attempted
        made_values = df[made_col].str.split('/', expand=True)[0].astype(float).fillna(0)
        att_values = df[made_col].str.split('/', expand=True)[1].astype(float).fillna(0)

        # Calculate the weighted score: made/attempted ratio * weight
        df['Weighted Score'] += (made_values / att_values.replace(0, 1)) * weight
        
    # Normalize the weighted score to a 0-100 scale
    score_range = df['Weighted Score'].max() - df['Weighted Score'].min()
    if score_range != 0:
        df['Weighted Score'] = ((df['Weighted Score'] - df['Weighted Score'].min()) / score_range) * 100
    else:
        df['Weighted Score'] = 100  # Default value if all scores are the same

    # Find the top kicker based on total field goal attempts
    top_kicker_att = df['Att'].max()
    if top_kicker_att != 0:
        df['FG Attempts % of Top'] = df['Att'] / top_kicker_att
    else:
        df['FG Attempts % of Top'] = 0  # If no attempts, set to 0

    # Adjust the weighted score to include the percentage of top kicker's attempts
    df['Weighted Score'] *= df['FG Attempts % of Top']

    # Rank the top kickers by Weighted Score
    bestKickers = df.nlargest(10, 'Weighted Score')

    # Save the top kickers to a new CSV file
    # bestKickers.to_csv('official_kicker_stats.csv', index=False)

    return bestKickers

def get_passing_stats():
    """
    Function to scrape passing stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped passing stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/passing/2024/reg/all/passingyards/desc"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    return df

def find_best_qbs(df):
    """
    Function to find the best quarterbacks based on passing yards, touchdowns, yards per attempt, and completion percentage.
    Args:
        df (DataFrame): A pandas DataFrame containing the passing stats.
    Returns:
        bestQBs (DataFrame): A pandas DataFrame containing the top quarterbacks ranked by a composite score.
    """
    # Convert passing yards and touchdowns to numeric values
    df['Pass Yards'] = df['Pass Yds'].str.replace(',', '').astype(int)
    df['TD'] = df['TD'].astype(int)
    df['Yds/Att'] = df['Yds/Att'].astype(float)
    df['Cmp %'] = df['Cmp %'].astype(float)
    df['INT'] = df['INT'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Pass Yards'] * 0.45) + 
        (df['TD'] * 0.4) + 
        (df['Yds/Att'] * 0.15) + 
        (df['Cmp %'] * 0.15)+
        (df['INT'] * 0.2)
    )
    
    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort quarterbacks by the composite score in descending order
    bestQBs = df.sort_values(by='Weighted Score', ascending=False).head(10)

    # Print the top quarterbacks
    # print(bestQBs)

    # Optionally, save the top quarterbacks to a new CSV file
    # bestQBs.to_csv('official_qb_stats.csv', index=False)

    return bestQBs

def get_rushing_stats():
    """
    Function to scrape rushing stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped rushing stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/rushing/2024/reg/all/rushingyards/desc"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    return df

def find_best_rbs(df):
    """
    Function to find the best running backs based on rushing yards, touchdowns, yards per carry, and fumbles.
    Args:
        df (DataFrame): A pandas DataFrame containing the rushing stats.
        Returns:
        bestRBs (DataFrame): A pandas DataFrame containing the top running backs ranked by a composite score.
    """
    # Convert rushing yards and touchdowns to numeric values
    df['Rush Yds'] = df['Rush Yds'].str.replace(',', '').astype(int)
    df['TD'] = df['TD'].astype(int)
    df['Att'] = df['Att'].astype(int)
    df['Rush FUM'] = df['Rush FUM'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Rush Yds'] * 0.45) + 
        (df['TD'] * 0.45) + 
        (df['Att'] * 0.1) +
        (df['Rush FUM'] * 0.2)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort running backs by the composite score in descending order
    bestRBs = df.sort_values(by='Weighted Score', ascending=False).head(10)

    # Print the top running backs
    # print(bestRBs)

    # Optionally, save the top running backs to a new CSV file
    # bestRBs.to_csv('official_rb_stats.csv', index=False)

    return bestRBs

def get_receiving_stats():
    """
    Function to scrape receiving stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped receiving stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/receiving/2024/reg/all/receivingreceptions/desc"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    player_data = []
    for row in table.find_all("tr")[1:]:  # Skip the header row
        player = [td.get_text().strip() for td in row.find_all("td")]
        player_data.append(player)
    df = pd.DataFrame(player_data, columns=headers)
    return df

def find_best_wrs(df):
    """
    Function to find the best wide receivers based on receiving yards, receptions, yards per reception, and touchdowns.
    Args:
        df (DataFrame): A pandas DataFrame containing the receiving stats.
    Returns:
        bestWRs (DataFrame): A pandas DataFrame containing the top wide receivers ranked by a composite score.
    """
    # Convert receiving yards, receptions, and touchdowns to numeric values
    df['Tgts'] = df['Tgts'].astype(int)
    df['Rec'] = df['Rec'].astype(int)
    df['Yds'] = df['Yds'].astype(float)
    df['TD'] = df['TD'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Rec'] * 0.35) + 
        (df['Yds'] * 0.15) + 
        (df['TD'] * 0.15) + 
        (df['Tgts'] * 0.1)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort wide receivers by the composite score in descending order
    bestWRs = df.sort_values(by='Weighted Score', ascending=False).head(10)

    # Print the top wide receivers
    # print(bestWRs)

    # Optionally, save the top wide receivers to a new CSV file
    # bestWRs.to_csv('official_wr_stats.csv', index=False)

    return bestWRs


# Scrape kicking stats
kicking_df = get_kicking_stats()
top_kickers = find_best_kickers(kicking_df)

print(f"Kicking DataFrame:") 
print(top_kickers)  # Print the top kickers
print("\n")

print("Scraping passing stats...")
passing_df = get_passing_stats()
top_qbs = find_best_qbs(passing_df)
print(f"Passing DataFrame:")
print(top_qbs)  # Print the first 10 rows of the passing DataFrame
print("\n")

print("Scraping rushing stats...")
rushing_df = get_rushing_stats()
top_rbs = find_best_rbs(rushing_df)
print(f"Rushing DataFrame:")
print(top_rbs)  # Print the first 10 rows of the rushing DataFrame
print("\n")

print("Scraping receiving stats...")
receiving_df = get_receiving_stats()
top_wrs = find_best_wrs(receiving_df)
print(f"Receiving DataFrame:")
print(top_wrs)  # Print the first 10 rows of the receiving DataFrame


