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
    return df
