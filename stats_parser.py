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
    print(df.columns)
    return df

def find_best_kickers(df):
    """
    Function to find the best kicker based on a kicker score that incorporates field goal percentage and distance ranges.
    Args:
        df (DataFrame): A pandas DataFrame containing the kicking stats.
    Returns:
        bestKickers (DataFrame): A pandas DataFrame containing the top kickers ranked by their kicker score.
    """
    # List of distance ranges with corresponding weights
    distance_ranges = {
        "20-29": 1.0,
        "30-39": 0.75,
        "40-49": 0.5,
        "50-59": 0.3,
        "60+": 0.25
    }

    # Initialize columns for total field goals made, attempts, and weighted score
    df['Total FGM'] = 0
    df['Total Att'] = 0
    df['Weighted Score'] = 0

    # Iterate through the distance ranges and calculate weighted scores
    for distance, weight in distance_ranges.items():
        made_col = f"{distance} > A-M"
        att_col = f"{distance} > A-M"

        # Convert FGM and Att columns to integers, ignoring rows where they're not available
        df[made_col] = pd.to_numeric(df[made_col], errors='coerce').fillna(0).astype(int)
        df[att_col] = pd.to_numeric(df[att_col], errors='coerce').fillna(0).astype(int)

        # Update totals and weighted score
        df['Total FGM'] += df[made_col]
        df['Total Att'] += df[att_col]
        df['Weighted Score'] += (df[made_col] / df[att_col].replace(0, 1)) * weight * df[made_col]

    # Calculate overall field goal percentage
    df['FG%'] = df['Total FGM'] / df['Total Att'].replace(0, 1)

    # Rank the top kickers by Weighted Score
    bestKickers = df.nlargest(10, 'Weighted Score')

    return bestKickers



# URLs for different categories
urls = {
    "Passing": "https://www.nfl.com/stats/player-stats/category/passing/2024/reg/all/passingyards/desc",
    "Rushing": "https://www.nfl.com/stats/player-stats/category/rushing/2024/reg/all/rushingyards/desc",
    "Receiving": "https://www.nfl.com/stats/player-stats/category/receiving/2024/reg/all/receivingreceptions/desc",
}

dataframes = {}

for category, url in urls.items():
    print(f"Scraping data from {category} category...")
    df = get_stats(url)
    if df is not None:
        dataframes[category] = df
        print(f"{category} DataFrame:")
        print(df.head(10))  # Print the first 10 rows of each DataFrame
        print("\n")

for category, df in dataframes.items():
    df.to_csv(f"nfl_player_stats_{category.lower().replace(' ', '_')}.csv", index=False)

# Scrape kicking stats
kicking_df = get_kicking_stats()
top_kickers = find_best_kickers(kicking_df)

print(f"Kicking DataFrame:") 
print(top_kickers)  # Print the top kickers
