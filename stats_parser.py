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
        "50-59": 0.4,
        "60+": 0.1,
    }

    # Initialize columns for total field goals made, attempts, and weighted score
    df['Total FGM'] = 0
    df['Total Att'] = 0
    df['Weighted Score'] = 0

    # Iterate through the distance ranges and calculate weighted scores
    for distance, weight in distance_ranges.items():
        made_col = f"{distance} > A-M"
        att_col = f"{distance} > A-M"

        # Split made/attempted values into separate columns for made and attempted
        made_values = df[made_col].str.split('/', expand=True)[0].astype(float).fillna(0)
        att_values = df[made_col].str.split('/', expand=True)[1].astype(float).fillna(0)

        # Update the dataframe with the parsed made and attempted values
        df[made_col] = made_values
        df[att_col] = att_values

        # Update totals and weighted score
        df['Total FGM'] += df[made_col]
        df['Total Att'] += df[att_col]

        # Calculate the weighted score: made/attempted ratio * weight
        df['Weighted Score'] += (df[made_col] / df[att_col].replace(0, 1)) * weight

    # Calculate overall field goal percentage
    df['FG%'] = df['Total FGM'] / df['Total Att'].replace(0, 1)

    # Find the top kicker based on total field goal attempts
    top_kicker_att = df['Total Att'].max()

    # Calculate the field goal attempts percentage of the top kicker's attempts
    df['FG Attempts % of Top'] = df['Total Att'] / top_kicker_att

    # Adjust the weighted score to include the percentage of top kicker's attempts
    df['Weighted Score'] *= df['FG Attempts % of Top']

    # Rank the top kickers by Weighted Score
    bestKickers = df.nlargest(10, 'Weighted Score')

    # Save the top kickers to a new CSV file
    bestKickers.to_csv('official_kicker_stats.csv', index=False)

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
        (df['TD'] * 0.35) + 
        (df['Yds/Att'] * 0.15) + 
        (df['Cmp %'] * 0.15) +
        (df['INT'] * 0.15)
    )
    
    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort quarterbacks by the composite score in descending order
    bestQBs = df.sort_values(by='Weighted Score', ascending=False).head(10)

    # Print the top quarterbacks
    print(bestQBs)

    # Optionally, save the top quarterbacks to a new CSV file
    # bestQBs.to_csv('official_qb_stats.csv', index=False)

    return bestQBs


# URLs for different categories
urls = {
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

# Save the dataframes to CSV files
# for category, df in dataframes.items():
#     df.to_csv(f"nfl_player_stats_{category.lower().replace(' ', '_')}.csv", index=False)

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

