"""
NFL Offensive Stats Analyzer
Author: Patrick Mejia
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_kicking_stats():
    """
    Function to scrape kicking stats from the NFL website.
    Returns: df (DataFrame): A pandas DataFrame containing the scraped kicking stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/field-goals/2024/reg/all/kickingfgmade/desc"
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


def find_best_kickers(df):
    """
    Function to find the best kicker based on a kicker score that incorporates field goal percentage,
    distance ranges, and field goal attempts as a percentage of the top kicker's attempts.
    Args:
        df (DataFrame): A pandas DataFrame containing the kicking stats.
    Returns:
        best_kickers (DataFrame): A pandas DataFrame containing the top kickers ranked by their kicker score.
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
    df["Weighted Score"] = 0
    df["FGM"] = df["FGM"].astype(int)
    df["Att"] = df["Att"].astype(int)

    # Iterate through the distance ranges and calculate weighted scores
    for distance, weight in distance_ranges.items():
        made_col = f"{distance} > A-M"

        # Split made/attempted values into separate columns for made and attempted
        made_values = (
            df[made_col].str.split("/", expand=True)[0].astype(float).fillna(0)
        )
        att_values = df[made_col].str.split("/", expand=True)[1].astype(float).fillna(0)

        # Calculate the weighted score: made/attempted ratio * weight
        df["Weighted Score"] += (made_values / att_values.replace(0, 1)) * weight

    # Normalize the weighted score to a 0-100 scale
    score_range = df["Weighted Score"].max() - df["Weighted Score"].min()
    if score_range != 0:
        df["Weighted Score"] = (
            (df["Weighted Score"] - df["Weighted Score"].min()) / score_range
        ) * 100
    else:
        df["Weighted Score"] = 100  # Default value if all scores are the same

    # Find the top kicker based on total field goal attempts
    top_kicker_att = df["Att"].max()
    if top_kicker_att != 0:
        df["FG Attempts % of Top"] = df["Att"] / top_kicker_att * 100
    else:
        df["FG Attempts % of Top"] = 0  # If no attempts, set to 0

    # Adjust the weighted score to include the percentage of top kicker's attempts
    df["Weighted Score"] += df["FG Attempts % of Top"]

    # Rank the top kickers by Weighted Score
    best_kickers = df.nlargest(32, "Weighted Score")

    # Save the top kickers to a new CSV file
    # best_kickers.to_csv('official_kicker_stats.csv', index=False)

    return best_kickers


def get_passing_stats():
    """
    Function to scrape passing stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped passing stats.
    """
    url = "https://www.nfl.com/stats/player-stats/category/passing/2024/reg/all/passingyards/desc"
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


def find_best_qbs(df):
    """
    Function to find the best quarterbacks based on passing yards, touchdowns, yards per attempt, and completion percentage.
    Args:
        df (DataFrame): A pandas DataFrame containing the passing stats.
    Returns:
        best_qbs (DataFrame): A pandas DataFrame containing the top quarterbacks ranked by a composite score.
    """
    # Convert passing yards and touchdowns to numeric values
    # Convert relevant columns to numeric values
    df["Pass Yards"] = pd.to_numeric(df["Pass Yds"].str.replace(",", ""), errors='coerce').fillna(0).astype(int)
    df["TD"] = pd.to_numeric(df["TD"], errors='coerce').fillna(0).astype(int)
    df["Yds/Att"] = pd.to_numeric(df["Yds/Att"], errors='coerce').fillna(0).astype(float)
    df["Cmp %"] = pd.to_numeric(df["Cmp %"], errors='coerce').fillna(0).astype(float)
    df["INT"] = pd.to_numeric(df["INT"], errors='coerce').fillna(0).astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["Pass Yards"] * 0.45)
        + (df["TD"] * 0.4)
        + (df["Yds/Att"] * 0.15)
        + (df["Cmp %"] * 0.15)
        + (df["INT"] * 0.2)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort quarterbacks by the composite score in descending order
    best_qbs = df.sort_values(by="Weighted Score", ascending=False).head(25)

    # Print the top quarterbacks
    # print(best_qbs)

    # Optionally, save the top quarterbacks to a new CSV file
    # best_qbs.to_csv('official_qb_stats.csv', index=False)

    return best_qbs


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
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(
                f"Failed to retrieve data from {url}. Status code: {response.status_code}"
            )
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
    df = (
        pd.DataFrame(player_data, columns=headers)
        if headers
        else pd.DataFrame(player_data)
    )
    return df


def find_best_rbs(df):
    """
    Function to find the best running backs based on rushing yards, touchdowns, yards per carry, and fumbles.
    Args:
        df (DataFrame): A pandas DataFrame containing the rushing stats.
        Returns:
        best_rbs (DataFrame): A pandas DataFrame containing the top running backs ranked by a composite score.
    """
    # Convert rushing yards and touchdowns to numeric values
    df["Rush Yds"] = df["Rush Yds"].str.replace(",", "").astype(int)
    df["TD"] = df["TD"].astype(int)
    df["Att"] = df["Att"].astype(int)
    df["Rush FUM"] = df["Rush FUM"].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["Rush Yds"] * 0.35)
        + (df["TD"] * 0.6)
        + (df["Att"] * 0.1)
        + (df["Rush FUM"] * 0.2)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort running backs by the composite score in descending order
    best_rbs = df.sort_values(by="Weighted Score", ascending=False).head(35)

    # Print the top running backs
    # print(best_rbs)

    # Optionally, save the top running backs to a new CSV file
    # best_rbs.to_csv('official_rb_stats.csv', index=False)

    return best_rbs


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
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(
                f"Failed to retrieve data from {url}. Status code: {response.status_code}"
            )
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
    df = (
        pd.DataFrame(player_data, columns=headers)
        if headers
        else pd.DataFrame(player_data)
    )
    return df


def find_best_wrs(df):
    """
    Function to find the best wide receivers based on receiving yards, receptions, yards per reception, and touchdowns.
    Args:
        df (DataFrame): A pandas DataFrame containing the receiving stats.
    Returns:
        best_wrs (DataFrame): A pandas DataFrame containing the top wide receivers ranked by a composite score.
    """
    # Convert receiving yards, receptions, and touchdowns to numeric values
    # Convert relevant columns to numeric values
    df["Tgts"] = pd.to_numeric(df["Tgts"], errors='coerce').fillna(0).astype(int)
    df["Rec"] = pd.to_numeric(df["Rec"], errors='coerce').fillna(0).astype(int)
    df["Yds"] = pd.to_numeric(df["Yds"].str.replace(",", ""), errors='coerce').fillna(0).astype(float)
    df["TD"] = pd.to_numeric(df["TD"], errors='coerce').fillna(0).astype(int)
    df["20+"] = pd.to_numeric(df["20+"], errors='coerce').fillna(0).astype(int)
    df["40+"] = pd.to_numeric(df["40+"], errors='coerce').fillna(0).astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["Rec"] * 0.35)
        + (df["Yds"] * 0.25)
        + (df["TD"] * 0.5)
        + (df["Tgts"] * 0.1)
        + (df["20+"] * 0.2)
        + (df["40+"] * 0.1)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort wide receivers by the composite score in descending order
    best_wrs = df.sort_values(by="Weighted Score", ascending=False).head(35)

    # Print the top wide receivers
    # print(best_wrs)

    # Optionally, save the top wide receivers to a new CSV file
    # best_wrs.to_csv('official_wr_stats.csv', index=False)

    return best_wrs


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
    # best_matchups.to_csv('official_matchup_stats.csv', index=False)

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
    # best_matchups.to_csv('official_matchup_stats.csv', index=False)

    return best_matchups


def main():
    """
    Main function to scrape and analyze NFL player and team stats.
    """
    # Scrape kicking stats
    print("Scraping kicking stats...")
    kicking_df = get_kicking_stats()
    top_kickers = find_best_kickers(kicking_df)
    print(top_kickers)  # Print the top kickers
    print("\n")

    print("Scraping passing stats...")
    passing_df = get_passing_stats()
    top_qbs = find_best_qbs(passing_df)
    print(top_qbs)  # Print the top quarterbacks
    print("\n")

    print("Scraping rushing stats...")
    rushing_df = get_rushing_stats()
    top_rbs = find_best_rbs(rushing_df)
    print(top_rbs)  # Print the top running backs
    print("\n")

    print("Scraping receiving stats...")
    receiving_df = get_receiving_stats()
    top_wrs = find_best_wrs(receiving_df)
    print(top_wrs)  # Print the top wide receivers
    print("\n")

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


if __name__ == "__main__":
    main()
