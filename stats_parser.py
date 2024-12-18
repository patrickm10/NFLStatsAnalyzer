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
        df['FG Attempts % of Top'] = df['Att'] / top_kicker_att * 100
    else:
        df['FG Attempts % of Top'] = 0  # If no attempts, set to 0

    # Adjust the weighted score to include the percentage of top kicker's attempts
    df['Weighted Score'] += df['FG Attempts % of Top']

    # Rank the top kickers by Weighted Score
    bestKickers = df.nlargest(32, 'Weighted Score')

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
    bestQBs = df.sort_values(by='Weighted Score', ascending=False).head(25)

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
    base_url = "https://www.nfl.com/stats/player-stats/category/rushing/2024/reg/all/rushingyards/desc"
    player_data = []
    headers = []

    aftercursor = None
    pages_scraped = 0
    max_pages = 3  # Limit to the first 3 pages

    while pages_scraped < max_pages:
        # Construct URL with aftercursor if it's available
        url = f"{base_url}?aftercursor={aftercursor}" if aftercursor else base_url

        # Make the request
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", class_="d3-o-table")
        if not table:
            print(f"No table found on {url}.")
            break

        # Extract headers (only once)
        if not headers:
            headers = [th.get_text().strip() for th in table.find_all("th")]

        # Extract player data
        for row in table.find_all("tr")[1:]:  # Skip the header row
            player = [td.get_text().strip() for td in row.find_all("td")]
            player_data.append(player)

        # Find the aftercursor value for the next page
        next_button = soup.find("a", class_="nfl-o-table-pagination__next")
        if next_button:
            aftercursor = next_button.get("href").split("aftercursor=")[-1]
        else:
            print("No more pages to scrape.")
            break

        pages_scraped += 1

    # Create a DataFrame
    df = pd.DataFrame(player_data, columns=headers) if headers else pd.DataFrame(player_data)
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
        (df['Rush Yds'] * 0.35) + 
        (df['TD'] * 0.6) + 
        (df['Att'] * 0.1) +
        (df['Rush FUM'] * 0.2)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort running backs by the composite score in descending order
    bestRBs = df.sort_values(by='Weighted Score', ascending=False).head(35)

    # Print the top running backs
    # print(bestRBs)

    # Optionally, save the top running backs to a new CSV file
    # bestRBs.to_csv('official_rb_stats.csv', index=False)

    return bestRBs

def get_receiving_stats():
    """
    Scrapes receiving stats from the NFL website, handling pagination with aftercursor.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the receiving stats.
    """
    base_url = "https://www.nfl.com/stats/player-stats/category/receiving/2024/REG/all/receivingreceptions/DESC"
    player_data = []
    headers = []

    aftercursor = None
    pages_scraped = 0
    max_pages = 3  # Limit to the first 3 pages

    while pages_scraped < max_pages:
        # Construct URL with aftercursor if it's available
        url = f"{base_url}?aftercursor={aftercursor}" if aftercursor else base_url

        # Make the request
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the table
        table = soup.find("table", class_="d3-o-table")
        if not table:
            print(f"No table found on {url}.")
            break

        # Extract headers (only once)
        if not headers:
            headers = [th.get_text().strip() for th in table.find_all("th")]

        # Extract player data
        for row in table.find_all("tr")[1:]:  # Skip the header row
            player = [td.get_text().strip() for td in row.find_all("td")]
            player_data.append(player)

        # Find the aftercursor value for the next page
        next_button = soup.find("a", class_="nfl-o-table-pagination__next")
        if next_button:
            aftercursor = next_button.get("href").split("aftercursor=")[-1]
        else:
            print("No more pages to scrape.")
            break

        pages_scraped += 1

    # Create a DataFrame
    df = pd.DataFrame(player_data, columns=headers) if headers else pd.DataFrame(player_data)
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
    df['20+'] = df['20+'].astype(int)
    df['40+'] = df['40+'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Rec'] * 0.35) + 
        (df['Yds'] * 0.25) + 
        (df['TD'] * 0.5) + 
        (df['Tgts'] * 0.1) +
        (df['20+'] * 0.2) +
        (df['40+'] * 0.1)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort wide receivers by the composite score in descending order
    bestWRs = df.sort_values(by='Weighted Score', ascending=False).head(35)

    # Print the top wide receivers
    # print(bestWRs)

    # Optionally, save the top wide receivers to a new CSV file
    # bestWRs.to_csv('official_wr_stats.csv', index=False)

    return bestWRs

def get_defensive_stats_versus_receiving():
    """
    Function to scrape defensive stats versus receiving stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped defensive versus receiving stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/receiving/2024/reg/all"
    defense_data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:  # Skip the header row
        defense = [td.get_text().strip() for td in row.find_all("td")]
        defense_data.append(defense)
    df = pd.DataFrame(defense_data, columns=headers)
    return df

def find_best_defenses_versus_receiving(df):
    """
    Function to find the best defenses against receiving based on yards allowed, touchdowns allowed, and interceptions.
    Args:
        df (DataFrame): A pandas DataFrame containing the defensive stats versus receiving.
    Returns:
        bestDefenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert receiving yards allowed, touchdowns allowed, and interceptions to numeric values
    df['Yds/Rec'] = df['Yds/Rec'].astype(float)
    df['Yds'] = df['Yds'].astype(int)
    df['TD'] = df['TD'].astype(int)
    df['Rec FUM'] = df['Rec FUM'].astype(int)
    df['PDef'] = df['PDef'].astype(int)
    df['20+'] = df['20+'].astype(int)
    df['40+'] = df['40+'].astype(int)
    

    # Calculate a composite score based on weighted stats 
    df['Score'] = (
        (df['Yds/Rec'] * 0.2) + 
        (df['Yds'] * 0.3) +
        (df['TD'] * 0.6) + 
        (df['Rec FUM'] * 0.1) + 
        (df['PDef'] * 0.2) + # PDef is passes defended
        (df['40+'] * 0.2) + 
        (df['20+'] * 0.1)
        
    )

    df['Weighted Score'] = 100 - ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min()) * 100)

    # Remove null records or columns
    df.dropna(axis=0, how='any', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # Remove newline characters from the dataframe
    df.replace('\n', '', regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df['Team'] = df['Team'].str.split().str[0]

    # Sort defenses by the composite score in descending order
    bestDefenses = df.sort_values(by='Weighted Score', ascending=False,ignore_index=True).head(32)

    # Print the top defenses
    # print(bestDefenses)

    # Optionally, save the top defenses to a new CSV file
    # bestDefenses.to_csv('official_defense_stats.csv', index=False)

    return bestDefenses


def get_defensive_stats_versus_rushing():
    """
    Function to scrape defensive stats versus rushing stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped defensive versus rushing stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/rushing/2024/reg/all"
    defense_data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:  # Skip the header row
        defense = [td.get_text().strip() for td in row.find_all("td")]
        defense_data.append(defense)
    df = pd.DataFrame(defense_data, columns=headers)
    return df

def find_best_defenses_versus_rushing(df):
    """
    Function to find the best defenses against rushing based on yards allowed, touchdowns allowed, and interceptions.
    Args:
        df (DataFrame): A pandas DataFrame containing the defensive stats versus rushing.
        Returns:
        bestDefenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert rushing yards allowed, touchdowns allowed, and interceptions to numeric values
    df['YPC'] = df['YPC'].astype(float)
    df['Rush Yds'] = df['Rush Yds'].astype(int)
    df['TD'] = df['TD'].astype(int)
    df['Rush FUM'] = df['Rush FUM'].astype(int)
    df['20+'] = df['20+'].astype(int)
    df['40+'] = df['40+'].astype(int)

    # Calculate a composite score based on weighted stats 
    df['Score'] = (
        (df['YPC'] * 0.3) + 
        (df['Rush Yds'] * 0.3) +
        (df['TD'] * 0.6) + 
        (df['40+'] * 0.3) + 
        (df['20+'] * 0.2) +
        (df['Rush FUM'] * 0.1)
        
    )

    df['Weighted Score'] = 100 - ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min()) * 100)
    
    # Remove null records or columns
    df.dropna(axis=0, how='any', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # Remove newline characters from the dataframe
    df.replace('\n', '', regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df['Team'] = df['Team'].str.split().str[0]

    # Sort defenses by the composite score in descending order
    bestDefenses = df.sort_values(by='Weighted Score', ascending=False,ignore_index=True).head(32)

    # Print the top defenses
    # print(bestDefenses)

    # Optionally, save the top defenses to a new CSV file
    # bestDefenses.to_csv('official_defense_stats.csv', index=False)

    return bestDefenses

def get_interceptions_stats():
    url = "https://www.nfl.com/stats/team-stats/defense/interceptions/2024/reg/all"
    defense_data = []
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:  # Skip the header row
        defense = [td.get_text().strip() for td in row.find_all("td")]
        defense_data.append(defense)
    df = pd.DataFrame(defense_data, columns=headers)
    return df

def find_top_defense_interceptions(df):
    """
    Function to find the best defenses based on interceptions.
    Args:
        df (DataFrame): A pandas DataFrame containing the defensive stats versus interceptions.
        Returns:
        bestDefenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert interceptions to numeric values
    df['INT'] = df['INT'].astype(int)
    df['INT TD'] = df['INT TD'].astype(int)
    df['INT Yds'] = df['INT Yds'].astype(int)

    # Calculate a composite score based on weighted stats 
    df['Score'] = ((df['INT'] * .8)  + 
    (df['INT TD']) + 
    (df['INT Yds'] * 0.2)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Remove null records or columns
    df.dropna(axis=0, how='any', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)

    # Remove newline characters from the dataframe
    df.replace('\n', '', regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df['Team'] = df['Team'].str.split().str[0]

    # Sort defenses by the composite score in descending order
    bestDefenses = df.sort_values(by='Weighted Score', ascending=False,ignore_index=True).head(32)

    # Print the top defenses
    # print(bestDefenses)

    # Optionally, save the top defenses to a new CSV file
    # bestDefenses.to_csv('official_defense_stats.csv', index=False)

    return bestDefenses

def get_special_teams_stats():
    """
    Function to scrape special teams stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped special teams stats.
    """
    url = "https://www.nfl.com/stats/team-stats/special-teams/kickoff-returns/2024/reg/all"
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

def find_best_special_teams(df):
    """
    Function to find the best special teams based on a composite score of return yards, return touchdowns, and return average.
    Args:
        df (DataFrame): A pandas DataFrame containing the special teams stats.
    Returns:
        bestSpecialTeams (DataFrame): A pandas DataFrame containing the top special teams ranked by a composite score.
    """
    # Convert return yards, return touchdowns, and return average to numeric values
    # print(df.columns)
    df['Yds'] = df['Yds'].astype(int)
    df['KRet TD'] = df['KRet TD'].astype(int)
    df['Avg'] = df['Avg'].astype(float)
    df['FUM'] = df['FUM'].astype(int)
    df['Ret'] = df['Ret'].astype(int)
    df['20+'] = df['20+'].astype(int)
    df['40+'] = df['40+'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Yds'] * 0.4) + 
        (df['KRet TD'] * 0.6) + 
        (df['Avg'] * 0.2) +
        (df['FUM'] * 0.1) +
        (df['Ret'] * 0.2) +
        (df['20+'] * 0.2) +
        (df['40+'] * 0.1)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort special teams by the composite score in descending order
    bestSpecialTeams = df.sort_values(by='Weighted Score', ascending=False).head(32)

    # Print the top special teams
    # print(bestSpecialTeams)

    # Optionally, save the top special teams to a new CSV file
    # bestSpecialTeams.to_csv('official_special_teams_stats.csv', index=False)

    return bestSpecialTeams

def get_punting_stats():
    """
    Function to scrape punting stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped punting stats.
    """
    url = "https://www.nfl.com/stats/team-stats/special-teams/punt-returns/2024/reg/all"
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

def find_best_punt_receivers(df):
    """
    Function to find the best punters based on a composite score of punt yards, punts inside the 20, and net average.
    Args:
        df (DataFrame): A pandas DataFrame containing the punting stats.
        Returns:
        bestPunters (DataFrame): A pandas DataFrame containing the top punters ranked by a composite score.
    """
    # Convert punt yards, punts inside the 20, and net average to numeric values
    # print(df.columns)
    df['Yds'] = df['Yds'].astype(int)
    df['Avg'] = df['Avg'].astype(float)
    df['PRet T'] = df['PRet T'].astype(int)
    df['FC'] = df['FC'].astype(int)
    df['Ret'] = df['Ret'].astype(int)
    df['20+'] = df['20+'].astype(int)
    df['40+'] = df['40+'].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df['Score'] = (
        (df['Yds'] * 0.4) + 
        (df['20+'] * 0.6) + 
        (df['Avg'] * 0.2) +
        (df['Avg'] * 0.2) +
        (df['FC'] * 0.1) +
        (df['PRet T'] * 0.3) +
        (df['Ret'] * 0.2) +
        (df['20+'] * 0.2)
    )

    df['Weighted Score'] = ((df['Score'] - df['Score'].min()) / (df['Score'].max() - df['Score'].min())) * 100

    # Sort punters by the composite score in descending order
    bestPunters = df.sort_values(by='Weighted Score', ascending=False).head(32)

    # Print the top punters
    # print(bestPunters)

    # Optionally, save the top punters to a new CSV file
    # bestPunters.to_csv('official_punter_stats.csv', index=False)

    return bestPunters

def get_best_special_teams(df1, df2):
    """
    Function to find the best special teams based on a combination of return and punting stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the special teams return stats.
        df2 (DataFrame): A pandas DataFrame containing the special teams punting stats.
        Returns:
        bestSpecialTeams (DataFrame): A pandas DataFrame containing the top special teams ranked by a composite score.
    """
    # Normalize the scores for each category
    df1['Weighted Score'] = ((df1['Weighted Score'] - df1['Weighted Score'].min()) / (df1['Weighted Score'].max() - df1['Weighted Score'].min())) * 100
    df2['Weighted Score'] = ((df2['Weighted Score'] - df2['Weighted Score'].min()) / (df2['Weighted Score'].max() - df2['Weighted Score'].min())) * 100

    # Combine the scores for return and punting
    df1['Combined Score'] = df1['Weighted Score'] + df2['Weighted Score']
    
    # Remove null records or columns
    df1.dropna(axis=0, how='any', inplace=True)
    df1.dropna(axis=1, how='all', inplace=True)

    # Remove newline characters from the dataframe
    df1.replace('\n', '', regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df1['Team'] = df1['Team'].str.split().str[0]

    # Sort special teams by the combined score in descending order
    bestSpecialTeams = df1.sort_values(by='Combined Score', ascending=False, ignore_index=True).head(32)

    # Print the top special teams
    # print(bestSpecialTeams)

    # Optionally, save the top special teams to a new CSV file
    # bestSpecialTeams.to_csv('official_special_teams_stats.csv', index=False)

    return bestSpecialTeams


def get_best_overall_defenses(df1, df2, df3):
    """
    Function to find the best defenses overall based on a combination of rushing and receiving stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the defensive stats versus rushing.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats versus receiving.
        df3 (DataFrame): A pandas DataFrame containing the defensive interceptions.
        Returns:
        bestDefenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Normalize the scores for each category
    df1['Weighted Score'] = ((df1['Weighted Score'] - df1['Weighted Score'].min()) / (df1['Weighted Score'].max() - df1['Weighted Score'].min())) * 100
    df2['Weighted Score'] = ((df2['Weighted Score'] - df2['Weighted Score'].min()) / (df2['Weighted Score'].max() - df2['Weighted Score'].min())) * 100
    df3['Weighted Score'] = ((df3['Weighted Score'] - df3['Weighted Score'].min()) / (df3['Weighted Score'].max() - df3['Weighted Score'].min())) * 100

    # Combine the scores for rushing and receiving
    df1['Combined Score'] = df1['Weighted Score'] + df2['Weighted Score'] + df3['Weighted Score']

    # Remove null records or columns
    df1.dropna(axis=0, how='any', inplace=True)
    df1.dropna(axis=1, how='all', inplace=True)

    # Remove newline characters from the dataframe
    df1.replace('\n', '', regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df1['Team'] = df1['Team'].str.split().str[0]

    # Sort defenses by the combined score in descending order
    bestDefenses = df1.sort_values(by='Combined Score', ascending=False, ignore_index=True).head(32)

    # Print the top defenses
    # print(bestDefenses)

    # Optionally, save the top defenses to a new CSV file
    # bestDefenses.to_csv('official_defense_stats.csv', index=False)

    return bestDefenses


#TODO: Change function to use schedule vs defense stats
def find_best_wr_defense_matchups(df1, df2):
    """
    Function to find the best wide receiver versus defense matchups based on a combination of receiving and defense stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the receiving stats.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats.
        Returns:
        bestMatchups (DataFrame): A pandas DataFrame containing the top matchups ranked by a composite score.
    """
    # Normalize the scores for each category
    df1['Weighted Score'] = ((df1['Weighted Score'] - df1['Weighted Score'].min()) / (df1['Weighted Score'].max() - df1['Weighted Score'].min())) * 100
    df2['Weighted Score'] = ((df2['Weighted Score'] - df2['Weighted Score'].min()) / (df2['Weighted Score'].max() - df2['Weighted Score'].min())) * 100

    # Combine the scores for receiving and defense
    df1['Combined Score'] = df1['Weighted Score'] + df2['Weighted Score']

    # Sort matchups by the combined score in descending order
    bestMatchups = df1.sort_values(by='Combined Score', ascending=True).head(32)

    # Print the top matchups
    # print(bestMatchups)

    # Optionally, save the top matchups to a new CSV file
    # bestMatchups.to_csv('official_matchup_stats.csv', index=False)

    return bestMatchups

#TODO: Change function to use schedule vs defense stats
def find_best_rb_defense_matchups(df1, df2):
    """
    Function to find the best wide receiver versus defense matchups based on a combination of receiving and defense stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the receiving stats.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats.
        Returns:
        bestMatchups (DataFrame): A pandas DataFrame containing the top matchups ranked by a composite score.
    """
    # Normalize the scores for each category
    df1['Weighted Score'] = ((df1['Weighted Score'] - df1['Weighted Score'].min()) / (df1['Weighted Score'].max() - df1['Weighted Score'].min())) * 100
    df2['Weighted Score'] = ((df2['Weighted Score'] - df2['Weighted Score'].min()) / (df2['Weighted Score'].max() - df2['Weighted Score'].min())) * 100

    # Combine the scores for receiving and defense
    df1['Combined Score'] = df1['Weighted Score'] + df2['Weighted Score']

    # Sort matchups by the combined score in descending order
    bestMatchups = df1.sort_values(by='Combined Score', ascending=True).head(32)

    # Print the top matchups
    # print(bestMatchups)

    # Optionally, save the top matchups to a new CSV file
    # bestMatchups.to_csv('official_matchup_stats.csv', index=False)

    return bestMatchups



def main():
    # Scrape kicking stats
    print("Scraping kicking stats...")
    kicking_df = get_kicking_stats()
    top_kickers = find_best_kickers(kicking_df)
    print(top_kickers)  # Print the top kickers
    print("\n")

    print("Scraping passing stats...")
    passing_df = get_passing_stats()
    top_qbs = find_best_qbs(passing_df)
    print(top_qbs) # Print the top quarterbacks
    print("\n")

    print("Scraping rushing stats...")
    rushing_df = get_rushing_stats()
    top_rbs = find_best_rbs(rushing_df)
    print(top_rbs) # Print the top running backs
    print("\n")

    print("Scraping receiving stats...")
    receiving_df = get_receiving_stats()
    top_wrs = find_best_wrs(receiving_df)
    print(top_wrs)  # Print the top wide receivers
    print("\n")


    # Scrape defensive stats versus receiving
    defense_df = get_defensive_stats_versus_receiving()
    top_defenses_receiving = find_best_defenses_versus_receiving(defense_df)
    print(f"Best Defenses Against Receiving:")
    print(top_defenses_receiving)  # Print the top defenses against receiving
    print("\n")

    # Scrape defensive stats versus rushing
    defense_rushing_df = get_defensive_stats_versus_rushing()
    top_defenses_rushing = find_best_defenses_versus_rushing(defense_rushing_df)
    print(f"Best Defenses Against Rushing:")
    print(top_defenses_rushing)  # Print the top defenses against rushing
    print("\n")
    
    # Scrape defensive stats versus interceptions
    defense_interceptions_df = get_interceptions_stats()
    top_defenses_interceptions = find_top_defense_interceptions(defense_interceptions_df)
    print(f"Best Defenses For Interceptions:")
    print(top_defenses_interceptions)  # Print the top defenses against interceptions
    print("\n")

    # Scrape special teams stats
    # print("Scraping special teams stats...")
    special_teams_df = get_special_teams_stats()
    top_special_teams = find_best_special_teams(special_teams_df)
    # print(top_special_teams)  # Print the top special teams
    # print("\n")
    
    # Scrape punting stats
    #print("Scraping punting stats...")
    punting_df = get_punting_stats()
    top_punters = find_best_punt_receivers(punting_df)
    # print(top_punters)  # Print the top punters
    # print("\n")

    # Find the best special teams
    best_special_teams = get_best_special_teams(top_special_teams, top_punters)
    print(f"Top Return Special Teams:")
    print(best_special_teams)  # Print the top special teams
    print("\n")

    # Find the best overall defenses
    best_defenses = get_best_overall_defenses(top_defenses_rushing, top_defenses_receiving, top_defenses_interceptions)
    print(f"Best Overall Defenses:")
    print(best_defenses)  # Print the top overall defenses
    print("\n")

    # Find the best wide receiver versus defense matchups
    best_matchups = find_best_wr_defense_matchups(top_wrs, top_defenses_receiving)
    # print(f"Best Wide Receiver vs. Defense Matchups:")
    # print(best_matchups)  # Print the top matchups
    # print("\n")

    # Find the best running back versus defense matchups
    best_rb_matchups = find_best_rb_defense_matchups(top_rbs, top_defenses_rushing)
    # print(f"Best Running Back vs. Defense Matchups:")
    # print(best_rb_matchups)  # Print the top matchups
    # print("\n")

if __name__ == "__main__": 
    main()
