"""
NFL Stats Analyzer
Author: Patrick Mejia
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_defensive_stats_versus_receiving():
    """
    Function to scrape defensive stats versus receiving stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped defensive versus receiving stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/receiving/2024/reg/all"
    defense_data = []
    response = requests.get(url, timeout=10)
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
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert receiving yards allowed, touchdowns allowed, and interceptions to numeric values
    df["Yds/Rec"] = df["Yds/Rec"].astype(float)
    df["Yds"] = df["Yds"].astype(int)
    df["TD"] = df["TD"].astype(int)
    df["Rec FUM"] = df["Rec FUM"].astype(int)
    df["PDef"] = df["PDef"].astype(int)
    df["20+"] = df["20+"].astype(int)
    df["40+"] = df["40+"].astype(int)

    # Calculate a composite score based on weighted stats
    df["Score"] = (
        (df["Yds/Rec"] * 0.2)
        + (df["Yds"] * 0.3)
        + (df["TD"] * 0.6)
        + (df["Rec FUM"] * 0.1)
        + (df["PDef"] * 0.2)
        + (df["40+"] * 0.2)  # PDef is passes defended
        + (df["20+"] * 0.1)
    )

    df["Weighted Score"] = 100 - (
        (df["Score"] - df["Score"].min())
        / (df["Score"].max() - df["Score"].min())
        * 100
    )

    # Remove null records or columns
    df.dropna(axis=0, how="any", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df["Team"] = df["Team"].str.split().str[0]

    # Sort defenses by the composite score in descending order
    best_defenses = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def get_defensive_stats_versus_rushing():
    """
    Function to scrape defensive stats versus rushing stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped defensive versus rushing stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/rushing/2024/reg/all"
    defense_data = []
    response = requests.get(url, timeout=10)
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
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert rushing yards allowed, touchdowns allowed, and interceptions to numeric values
    df["YPC"] = df["YPC"].astype(float)
    df["Rush Yds"] = df["Rush Yds"].astype(int)
    df["TD"] = df["TD"].astype(int)
    df["Rush FUM"] = df["Rush FUM"].astype(int)
    df["20+"] = df["20+"].astype(int)
    df["40+"] = df["40+"].astype(int)

    # Calculate a composite score based on weighted stats
    df["Score"] = (
        (df["YPC"] * 0.3)
        + (df["Rush Yds"] * 0.3)
        + (df["TD"] * 0.6)
        + (df["40+"] * 0.3)
        + (df["20+"] * 0.2)
        + (df["Rush FUM"] * 0.1)
    )

    df["Weighted Score"] = 100 - (
        (df["Score"] - df["Score"].min())
        / (df["Score"].max() - df["Score"].min())
        * 100
    )

    # Remove null records or columns
    df.dropna(axis=0, how="any", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df["Team"] = df["Team"].str.split().str[0]

    # Sort defenses by the composite score in descending order
    best_defenses = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def get_interceptions_stats():
    """
    Function to scrape interceptions stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped interceptions stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/interceptions/2024/reg/all"
    defense_data = []
    response = requests.get(url, timeout=10)
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
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert interceptions to numeric values
    df["INT"] = df["INT"].astype(int)
    df["INT TD"] = df["INT TD"].astype(int)
    df["INT Yds"] = df["INT Yds"].astype(int)

    # Calculate a composite score based on weighted stats
    df["Score"] = (df["INT"] * 0.8) + (df["INT TD"]) + (df["INT Yds"] * 0.2)

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Remove null records or columns
    df.dropna(axis=0, how="any", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df["Team"] = df["Team"].str.split().str[0]

    # Sort defenses by the composite score in descending order
    best_defenses = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def get_fumbles_stats():
    """
    Function to scrape fumbles stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped fumbles stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/fumbles/2024/reg/all"
    defense_data = []
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:  # Skip the header row
        defense = [td.get_text().strip() for td in row.find_all("td")]
        defense_data.append(defense)
    df = pd.DataFrame(defense_data, columns=headers)
    return df


def find_top_defense_fumbles(df):
    """
    Function to find the best defenses based on fumbles.
    Args:
        df (DataFrame): A pandas DataFrame containing the defensive stats versus fumbles.
        Returns:
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert fumbles to numeric values
    df["FF"] = df["FF"].astype(int)
    df["FR"] = df["FR"].astype(int)
    df["FR TD"] = df["FR TD"].astype(int)

    # Calculate a composite score based on weighted stats
    df["Score"] = (df["FF"] * 0.5) + (df["FR"] * 0.5) + (df["FR TD"] * 0.3)

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Remove null records or columns
    df.dropna(axis=0, how="any", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df["Team"] = df["Team"].str.split().str[0]

    # Sort defenses by the composite score in descending order
    best_defenses = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def get_tackles_stats():
    """
    Function to scrape tackles stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped tackles stats.
    """
    url = "https://www.nfl.com/stats/team-stats/defense/tackles/2024/reg/all"
    defense_data = []
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table", class_="d3-o-table")
    headers = [th.get_text().strip() for th in table.find_all("th")]
    for row in table.find_all("tr")[1:]:  # Skip the header row
        defense = [td.get_text().strip() for td in row.find_all("td")]
        defense_data.append(defense)
    df = pd.DataFrame(defense_data, columns=headers)
    return df


def find_top_defense_tackles(df):
    """
    Function to find the best defenses based on tackles.
    Args:
        df (DataFrame): A pandas DataFrame containing the defensive stats versus tackles.
        Returns:
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
    """
    # Convert tackles to numeric values
    df["Sck"] = df["Sck"].astype(int)
    df["Solo"] = df["Solo"].astype(int)
    df["Comb"] = df["Comb"].astype(float)

    # Calculate a composite score based on weighted stats
    df["Score"] = (df["Sck"] * 0.5) + (df["Solo"] * 0.3) + (df["Comb"] * 0.5)

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Remove null records or columns
    df.dropna(axis=0, how="any", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df["Team"] = df["Team"].str.split().str[0]

    # Sort defenses by the composite score in descending order
    best_defenses = df.sort_values(
        by="Weighted Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def get_special_teams_stats():
    """
    Function to scrape special teams stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped special teams stats.
    """
    url = "https://www.nfl.com/stats/team-stats/special-teams/kickoff-returns/2024/reg/all"
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


def find_best_special_teams(df):
    """
    Function to find the best special teams based on a composite score of return yards, return touchdowns, and return average.
    Args:
        df (DataFrame): A pandas DataFrame containing the special teams stats.
    Returns:
        best_special_teams (DataFrame): A pandas DataFrame containing the top special teams ranked by a composite score.
    """
    # Convert return yards, return touchdowns, and return average to numeric values
    # print(df.columns)
    df["Yds"] = df["Yds"].astype(int)
    df["KRet TD"] = df["KRet TD"].astype(int)
    df["Avg"] = df["Avg"].astype(float)
    df["FUM"] = df["FUM"].astype(int)
    df["Ret"] = df["Ret"].astype(int)
    df["20+"] = df["20+"].astype(int)
    df["40+"] = df["40+"].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["Yds"] * 0.4)
        + (df["KRet TD"] * 0.6)
        + (df["Avg"] * 0.2)
        + (df["FUM"] * 0.1)
        + (df["Ret"] * 0.2)
        + (df["20+"] * 0.2)
        + (df["40+"] * 0.1)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort special teams by the composite score in descending order
    best_special_teams = df.sort_values(by="Weighted Score", ascending=False).head(32)

    # Print the top special teams
    # print(best_special_teams)

    # Optionally, save the top special teams to a new CSV file
    # best_special_teams.to_csv('official_special_teams_stats.csv', index=False)

    return best_special_teams


def get_punting_stats():
    """
    Function to scrape punting stats from the NFL website.
    Returns:
        df (DataFrame): A pandas DataFrame containing the scraped punting stats.
    """
    url = "https://www.nfl.com/stats/team-stats/special-teams/punt-returns/2024/reg/all"
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


def find_best_punt_receivers(df):
    """
    Function to find the best punters based on a composite score of punt yards, punts inside the 20, and net average.
    Args:
        df (DataFrame): A pandas DataFrame containing the punting stats.
        Returns:
        best_punters (DataFrame): A pandas DataFrame containing the top punters ranked by a composite score.
    """
    # Convert punt yards, punts inside the 20, and net average to numeric values
    # print(df.columns)
    df["Yds"] = df["Yds"].astype(int)
    df["Avg"] = df["Avg"].astype(float)
    df["PRet T"] = df["PRet T"].astype(int)
    df["FC"] = df["FC"].astype(int)
    df["Ret"] = df["Ret"].astype(int)
    df["20+"] = df["20+"].astype(int)
    df["40+"] = df["40+"].astype(int)

    # Calculate a composite score based on weighted stats (you can adjust the weights as needed)
    df["Score"] = (
        (df["Yds"] * 0.4)
        + (df["20+"] * 0.6)
        + (df["Avg"] * 0.2)
        + (df["Avg"] * 0.2)
        + (df["FC"] * 0.1)
        + (df["PRet T"] * 0.3)
        + (df["Ret"] * 0.2)
        + (df["20+"] * 0.2)
    )

    df["Weighted Score"] = (
        (df["Score"] - df["Score"].min()) / (df["Score"].max() - df["Score"].min())
    ) * 100

    # Sort punters by the composite score in descending order
    best_punters = df.sort_values(by="Weighted Score", ascending=False).head(32)

    # Print the top punters
    # print(best_punters)

    # Optionally, save the top punters to a new CSV file
    # best_punters.to_csv('official_punter_stats.csv', index=False)

    return best_punters


def get_best_special_teams(df1, df2):
    """
    Function to find the best special teams based on a combination of return and punting stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the special teams return stats.
        df2 (DataFrame): A pandas DataFrame containing the special teams punting stats.
        Returns:
        best_special_teams (DataFrame): A pandas DataFrame containing the top special teams ranked by a composite score.
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

    # Combine the scores for return and punting
    df1["Combined Score"] = df1["Weighted Score"] + df2["Weighted Score"]

    # Remove null records or columns
    df1.dropna(axis=0, how="any", inplace=True)
    df1.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df1.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df1["Team"] = df1["Team"].str.split().str[0]

    # Sort special teams by the combined score in descending order
    best_special_teams = df1.sort_values(
        by="Combined Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top special teams
    # print(best_special_teams)

    # Optionally, save the top special teams to a new CSV file
    # best_special_teams.to_csv('official_special_teams_stats.csv', index=False)

    return best_special_teams


def get_best_overall_defenses(df1, df2, df3):
    """
    Function to find the best defenses overall based on a combination of rushing and receiving stats.
    Args:
        df1 (DataFrame): A pandas DataFrame containing the defensive stats versus rushing.
        df2 (DataFrame): A pandas DataFrame containing the defensive stats versus receiving.
        df3 (DataFrame): A pandas DataFrame containing the defensive interceptions.
        Returns:
        best_defenses (DataFrame): A pandas DataFrame containing the top defenses ranked by a composite score.
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
    df3["Weighted Score"] = (
        (df3["Weighted Score"] - df3["Weighted Score"].min())
        / (df3["Weighted Score"].max() - df3["Weighted Score"].min())
    ) * 100

    # Combine the scores for rushing and receiving
    df1["Combined Score"] = (
        df1["Weighted Score"] + df2["Weighted Score"] + df3["Weighted Score"]
    )

    # Remove null records or columns
    df1.dropna(axis=0, how="any", inplace=True)
    df1.dropna(axis=1, how="all", inplace=True)

    # Remove newline characters from the dataframe
    df1.replace("\n", "", regex=True, inplace=True)

    # Remove everything after the first word for the team name
    df1["Team"] = df1["Team"].str.split().str[0]

    # Sort defenses by the combined score in descending order
    best_defenses = df1.sort_values(
        by="Combined Score", ascending=False, ignore_index=True
    ).head(32)

    # Print the top defenses
    # print(best_defenses)

    # Optionally, save the top defenses to a new CSV file
    # best_defenses.to_csv('official_defense_stats.csv', index=False)

    return best_defenses


def main():
    """
    Main function to scrape and analyze NFL player and team stats.
    """
    # Scrape defensive stats versus receiving
    defense_df = get_defensive_stats_versus_receiving()
    top_defenses_receiving = find_best_defenses_versus_receiving(defense_df)
    print("Best Defenses Against Receiving:")
    print(top_defenses_receiving)  # Print the top defenses against receiving
    print("\n")

    # Scrape defensive stats versus rushing
    defense_rushing_df = get_defensive_stats_versus_rushing()
    top_defenses_rushing = find_best_defenses_versus_rushing(defense_rushing_df)
    print("Best Defenses Against Rushing:")
    print(top_defenses_rushing)  # Print the top defenses against rushing
    print("\n")

    # Scrape defensive stats versus interceptions
    defense_interceptions_df = get_interceptions_stats()
    top_defenses_interceptions = find_top_defense_interceptions(
        defense_interceptions_df
    )
    print("Best Defenses For Interceptions:")
    print(top_defenses_interceptions)  # Print the top defenses against interceptions
    print("\n")

    # Scrape defensive stats fumbles
    defense_fumbles_df = get_fumbles_stats()
    top_defenses_fumbles = find_top_defense_fumbles(defense_fumbles_df)
    print("Best Defenses For Fumbles:")
    print(top_defenses_fumbles)  # Print the top defenses against fumbles
    print("\n")

    # Scrape defenses for tackles
    defense_tackles_df = get_tackles_stats()
    top_defenses_tackles = find_top_defense_tackles(defense_tackles_df)
    print("Best Defenses For Tackles:")
    print(top_defenses_tackles)  # Print the top defenses against tackles
    print("\n")

    # Scrape special teams stats
    # print("Scraping special teams stats...")
    special_teams_df = get_special_teams_stats()
    top_special_teams = find_best_special_teams(special_teams_df)
    # print(top_special_teams)  # Print the top special teams
    # print("\n")

    # Scrape punting stats
    # print("Scraping punting stats...")
    punting_df = get_punting_stats()
    top_punters = find_best_punt_receivers(punting_df)
    # print(top_punters)  # Print the top punters
    # print("\n")

    # Find the best special teams
    best_special_teams = get_best_special_teams(top_special_teams, top_punters)
    print("Top Return Special Teams:")
    print(best_special_teams)  # Print the top special teams
    print("\n")

    # Find the best overall defenses
    best_defenses = get_best_overall_defenses(
        top_defenses_rushing, top_defenses_receiving, top_defenses_interceptions
    )
    print("Best Overall Defenses:")
    print(best_defenses)  # Print the top overall defenses
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
