# FantasyPros ADP Stats Parser
# This script fetches the ADP stats from FantasyPros and saves it to a CSV file
# Author: Patrick Mejia

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ADPStatsParser:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def fetch_data(self, position):
        """Fetches the HTML content using requests with proper headers.
        Args:
            position (str): Position to fetch data for.
            Returns:
            str: HTML content of the page.
        """
        url = f"{self.base_url}?position={position}"
        logging.info(f"Fetching data from: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def parse_data(self, html_content):
        """Parses the HTML content and extracts table data.
        Args:
            html_content (str): HTML content to parse.
            Returns:
            list: List of column headers.
            list: List of rows of data.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Try to find the first table on the page
        table = soup.find("table")
        if not table:
            logging.warning("No table found in the page content.")
            return [], []

        # Extract headers
        headers = [th.get_text().strip() for th in table.find_all("th")]

        # Extract rows
        rows = table.find_all("tr")[1:]  # Skip header row
        data = [[td.get_text().strip() for td in row.find_all("td")] for row in rows]

        return headers, data

    def parse_position(self, position):
        """Fetch and parse ADP data for a given position.
        Args:
            position (str): Position to fetch data for.
            Returns:
            list: List of column headers.
            list: List of rows of data.
        """
        html_content = self.fetch_data(position)
        if not html_content:
            return [], []

        headers, data = self.parse_data(html_content)
        return headers, data

    def parse_all_positions(self):
        """Fetch and save ADP data for all positions.
        Iterates over all positions and saves the data to CSV files.
        """
        positions = ["QB", "RB", "WR", "TE"]
        for position in positions:
            headers, data = self.parse_position(position)
            if headers and data:
                self.save_to_csv(headers, data, f"adp_rankings_{position}.csv")
            else:
                logging.warning(f"No data found for {position}")

    def remove_team_from_name(self, name):
        """Removes the team name and other details from the player name.
        Args:
            name (str): Player name with team name and other details.
            Returns:
            str: Player name without team name and other details.
        """
        # Use regex to remove everything after multiple capitalized letters in a row
        return re.sub(r'\s+[A-Z]{2,}.*', '', name)

    def save_to_csv(self, headers, data, filename):
        """Saves the headers and data to a CSV file.
        Also removes the team name from the player name.
        Args:
            headers (list): List of column headers.
            data (list): List of rows of data.
            filename (str): Name of the output CSV file.
        Returns:
            None
        """

        df = pd.DataFrame(data, columns=headers)
        # df["Player"] = df["Player Team (Bye)"].apply(self.remove_team_from_name)

        df.to_csv(filename, index=False)
        logging.info(f"df: {df}")
        logging.info(f"Saved data to {filename}")

    def get_drafted_players_adp(self, adp_data, draft_picks):
        """Gets the drafted players and their ADP rankings.
        Args:
            adp_data (DataFrame): DataFrame containing ADP data.
            draft_picks (list): List of player names drafted.
            Returns:
            DataFrame: DataFrame of drafted players and their ADP rankings.
        """
        # Filter the ADP data for the drafted players
        drafted_players = adp_data[adp_data["Player"].isin([pick["Player"] for pick in draft_picks])]
        drafted_players = drafted_players.reset_index(drop=True)

        # Remove the header of table
        drafted_players = drafted_players.drop(drafted_players.index[0])
        drafted_players = drafted_players.drop(columns=['Rank', 'CBS', 'RTSports', 'Sleeper'])
        logging.info(f"Drafted players: {drafted_players}\n")

        # Ensure the drafted players are found in the ADP data
        # if len(drafted_players) != len(draft_picks):
        #     logging.error("Some drafted players not found in the ADP data.")
        #     return None

        # Ensure 'SLEEPER' column exists
        # if 'Sleeper' not in drafted_players.columns:
        #     logging.error("'Sleeper' column is missing from the ADP data.")
        #     return None

        # Ensure 'RTSPORTS' column exists
        # if 'RTSports' not in drafted_players.columns:
        #     logging.error("'RTSports' column is missing from the ADP data.")
        #     return None

        # Ensure 'Player' column exists
        if 'Player' not in drafted_players.columns:
            logging.error("'Player' column is missing from the ADP data.")
            return None

        return drafted_players

    def grade_draft_based_on_adp(self, drafted_players, draft_picks):
        """Grades a draft based on ADP data.
        Args:
            drafted_players (DataFrame): DataFrame containing drafted players and their ADP rankings.
            draft_picks (list): List of player names drafted.
            Returns:
            str: Draft grade.
        """
        # Gets the draft picks with their Sleeper ADP rankings
        try:
            # logging.info(f"Drafted players: {drafted_players}\n")
            draft_picks_adp = drafted_players["AVG"].astype(float).sum()
        except ValueError as e:
            logging.error(f"Draft picks ADP sum failed: {e}")
            return None

        # Calculate the total number of players drafted
        total_players = len(draft_picks)

        # Calculate the average difference
        avg_diff = draft_picks_adp / total_players

        # # Log the results
        # logging.info(f"Total difference: {draft_picks_adp}")
        logging.info(f"Total players: {total_players}")

        # # Grade the draft based on the average difference on a scale of 100
        # grade = 100 - avg_diff * 10  # Adjust the scale as needed

        # # Ensure the grade is within 0 to 100
        # grade = max(0, min(100, grade))

        return avg_diff

    def create_mock_draft_options(self, adp_data, draft_pick_number):
        """Creates a list of mock draft options for the given pick number.
        
        Draft order follows a snake format:
        Example: 1st pick, 22nd pick, 23rd pick, 44th pick, etc.

        Args:
            adp_data (DataFrame): DataFrame containing ADP data.
            draft_pick_number (int): Draft pick number.

        Returns:
            list: List of mock draft options per round for the given pick number.
        """
        if draft_pick_number < 1:
            logging.error("Draft pick number must be greater than 0.")
            return None

        num_teams = 10  # Number of teams in the league
        num_rounds = 14  # Total rounds in the draft
        total_picks = num_teams * num_rounds

        # Determine pick positions in the snake draft format
        pick_position = draft_pick_number % num_teams or num_teams
        logging.info(f"Your Draft Pick: {pick_position}\n")

        # Generate the snake draft order
        draft_order = []
        for round_num in range(num_rounds):
            round_picks = list(range(1, num_teams + 1)) if round_num % 2 == 0 else list(range(num_teams, 0, -1))
            draft_order.extend(round_picks)

        # Identify all pick positions for the given draft slot
        pick_positions = [draft_order[i] + num_teams * (i // num_teams) for i in range(draft_pick_number - 1, total_picks, num_teams)]
        logging.info(f"Pick positions: {pick_positions}\n")

        # Initialize draft selections
        mock_draft_options = []
        mock_draft_top_selections = []
        position_counts = {"RB": 0, "WR": 0, "TE": 0, "QB": 0, "DST": 0, "K": 0}
        max_positions = {"RB": 4, "WR": 3, "TE": 2, "QB": 2, "DST": 1, "K": 1}

        # Preferred draft order by position
        position_draft_order = ["RB", "WR", "WR", "RB", "WR", "QB", "RB", "QB", "DST", "K", "TE"]

        # Sort players by ADP (ascending order means best available first)
        adp_data_sorted = adp_data.sort_values(by="AVG", ascending=True)

        selected_players = set()

        for round_num, position in enumerate(position_draft_order):
            # Get the best available player who fits the position criteria and rank criteria
            best_available_player = None
            for _, player in adp_data_sorted.iterrows():
                player_position = player["POS"]
                main_position = re.match(r'[A-Z]+', player_position).group()  # Extract main position (e.g., RB1 -> RB)

                if main_position == position and position_counts[main_position] < max_positions[main_position]:
                    if player["Player"] not in selected_players and player["Rank"] > pick_positions[round_num]:
                        best_available_player = player["Player"]
                        position_counts[main_position] += 1
                        selected_players.add(player["Player"])
                        break
            logging.info(f"Selecting best available player for {position}...")
            if best_available_player:
                mock_draft_top_selections.append((best_available_player, position))
                logging.info(f"Round {round_num + 1}: {best_available_player}, {position}\n")

        logging.info(f"-------------------Player Selection Complete---------------------------------\n")

        return mock_draft_top_selections

    def run(self, position, output_file):
        """Runs the full process for a single position.
        Fetches, parses, and saves the data to a CSV file.
        Args:
            position (str): Position to fetch data for.
            output_file (str): Name of the output CSV file.
        Returns:
            None
        """
        headers, data = self.parse_position(position)
        if headers and data:
            self.save_to_csv(headers, data, output_file)
        else:
            logging.warning(f"No data found for {position}")

if __name__ == "__main__":
    # Run the parser
    base_url = "https://www.fantasypros.com/nfl/adp/overall.php"

    # Create an instance of the parser
    parser = ADPStatsParser(base_url)
    # parser.parse_all_positions()
    # logging.info("Parsing all positions...\n")

    # Grade a test draft
    try:
        adp_data = pd.read_csv("adp_rankings_RB.csv")
        draft_picks = [
        {"Pick": 1, "Player": "Christian McCaffrey"},
        {"Pick": 2, "Player": "Dalvin Cook"},
        {"Pick": 3, "Player": "Alvin Kamara"},
        {"Pick": 4, "Player": "Derrick Henry"},
        {"Pick": 5, "Player": "Antonio Gibson"},
    ]
        # drafted_players = parser.get_drafted_players_adp(adp_data, draft_picks)
        # grade = parser.grade_draft_based_on_adp(drafted_players, draft_picks)
    except Exception as e:
        logging.error(f"Draft grading failed: {e}")
        grade = None

    # Print the draft grade
    # logging.info(f"Draft grade: {grade}\n")

    # Create mock draft options
    try:
        mock_draft_options = parser.create_mock_draft_options(adp_data,3)
        # logging.info(f"Mock draft options: {mock_draft_options}\n")
    except Exception as e:
        logging.error(f"Mock draft options failed: {e}")
        mock_draft_options = None

