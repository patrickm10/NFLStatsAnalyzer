# FantasyPros ADP Stats Parser
# This script fetches the ADP stats from FantasyPros and saves it to a CSV file
# Author: Patrick Mejia

from bs4 import BeautifulSoup
import logging
import os
import re
import requests
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DraftCalculator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def fetch_data(self, position, year):
        """Fetches the HTML content using requests with proper headers.
        Args:
            position (str): Position to fetch data for.
            Returns:
            str: HTML content of the page.
        """
        url = f"{self.base_url}{position}.php?year={year}"
        logging.info(f"Fetching data from: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check if the response is successful
            if response.status_code != 200:
                logging.error(f"Failed to fetch data: {response.status_code}")
                return None
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

        logging.info(f"{data[:5]}")  # Log first 5 rows of data for debugging

        return headers, data

    def parse_position(self, position, year):
        """Fetch and parse ADP data for a given position.
        Args:
            position (str): Position to fetch data for.
            Returns:
            list: List of column headers.
            list: List of rows of data.
        """
        html_content = self.fetch_data(position, year)
        if not html_content:
            return [], []

        headers, data = self.parse_data(html_content)
        return headers, data

    def parse_all_positions(self, year):
        """Fetch and save ADP data for all positions into folders by year."""
        positions = ["QB", "RB", "WR", "TE"]
        for position in positions:
            headers, data = self.parse_position(position, year)
            if headers and data:
                filename = f"data/adp_data/{year}/{position}.csv"
                self.save_to_csv(headers, data, filename)
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

    
    def save_to_csv(self, headers, data, filename, split_by_position=False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df = pd.DataFrame(data, columns=headers)

        # Extract main position letters (e.g., from WR1 to WR)
        if "POS" in df.columns:
            df["Main_POS"] = df["POS"].str.extract(r'^([A-Z]+)')

        if split_by_position:
            if "POS" not in df.columns:
                logging.warning(f"'POS' column missing, cannot split by position for {filename}. Saving whole file.")
                df.to_csv(filename, index=False)
            else:
                for pos, group_df in df.groupby("Main_POS"):
                    pos_filename = filename.replace(".csv", f"_{pos}.csv")
                    group_df.drop(columns=["Main_POS"], inplace=True)  # Optional: drop helper col before saving
                    group_df.to_csv(pos_filename, index=False)
                    logging.info(f"Saved {pos} players to {pos_filename}")
                    logging.info(f"{df.head(5)}\n")
        else:
            df.to_csv(filename, index=False)
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
        drafted_players = drafted_players.drop(columns=['CBS', 'RTSports', 'Sleeper'])
        # logging.info(f"Drafted players: {drafted_players}\n")

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
        if draft_pick_number < 0:
            logging.error("Draft pick number must be greater than 0.")
            return None

        num_teams = 10  # Number of teams in the league
        num_rounds = 15  # Total rounds in the draft
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
        mock_draft_top_selections = []
        position_counts = {"RB": 0, "WR": 0, "TE": 0, "QB": 0, "DST": 0, "K": 0}
        max_positions = {"RB": 4, "WR": 4, "TE": 2, "QB": 2, "DST": 1, "K": 1}

        # Preferred draft order by position
        position_draft_order = ["RB", "WR", "RB", "WR" ,"TE", "QB", "WR", "RB", "WR", "QB", "K", "DST", "TE", "RB"]

        # Sort players by ADP (ascending order means best available first)
        adp_data_sorted = adp_data.sort_values(by="AVG", ascending=True)

        selected_players = set()

        for round_num, position in enumerate(position_draft_order):
            top_options = []  # Store top 3 available players per position
            best_available_player = None  # Best available pick to be added to final selection

            # Iterate through sorted players to find top 3 for the given position
            for _, player in adp_data_sorted.iterrows():
                player_position = player["POS"]
                main_position = re.match(r'[A-Z]+', player_position).group()  # Extract main position (e.g., RB1 -> RB)

                if (main_position == position and position_counts[main_position] < max_positions[main_position]
                    and player["Player"] not in selected_players 
                    and player["Rank"] >= pick_positions[round_num]):  # Ensures pick is valid for this round
                    
                    top_options.append(player["Player"])  # Add player to top picks
                    selected_players.add(player["Player"])

                    if len(top_options) == 3:  # Stop once we have 3 options
                        break

            if not top_options:
                logging.warning(f"No valid pick found for Round {round_num + 1}. Selecting best available player.")
                for _, player in adp_data_sorted.iterrows():  # Iterate through sorted ADP data
                    if player["Player"] not in selected_players:  # Pick first available player
                        best_available_player = player["Player"]
                        selected_players.add(best_available_player)
                        break
            else:
                best_available_player = top_options[0]  # Assign best available player from top options

            if best_available_player:
                position_counts[position] += 1
                # mock_draft_top_selections.append((best_available_player, position))

            # logging.info(f"Round {round_num + 1}: Best - {best_available_player}, "
            #             f"Next: {top_options[1] if len(top_options) > 1 else 'N/A'}, "
            #             f"Third: {top_options[2] if len(top_options) > 2 else 'N/A'}\n")

            # Best available player is added to the final selection
            # logging.info(f"Round {round_num + 1} Selection: {best_available_player}\n")
            mock_draft_top_selections.append((best_available_player, position))

            # Log the mock draft selections by name only
            player_names = []
            
            for player in mock_draft_top_selections:
                player_names.append(player[0])
                # logging.info(player)

        logging.info(f"------------------- Player Selection Complete ---------------------------------\n")

        return player_names

    def simulate_snake_draft(self, adp_data, num_teams=10, num_rounds=15):
        """Simulates a snake draft based on ADP data and assigns players to teams.
        Args:
            adp_data (DataFrame): DataFrame containing ADP data.
            num_teams (int): Number of teams in the league.
            num_rounds (int): Number of rounds in the draft.
        Returns:
            dict: Dictionary of teams with their drafted players and grades.
        """
        total_picks = num_teams * num_rounds
        draft_order = []

        # Generate the snake draft order
        for round_num in range(num_rounds):
            round_picks = list(range(1, num_teams + 1)) if round_num % 2 == 0 else list(range(num_teams, 0, -1))
            draft_order.extend(round_picks)

        # Initialize draft selections
        teams = {f"Team {i+1}": [] for i in range(num_teams)}
        selected_players = set()

        for i in range(total_picks):
            pick_position = draft_order[i]
            team_name = f"Team {pick_position}"
            round_number = (i // num_teams) + 1
            # logging.info(f"Pick {i + 1} (Round {round_number}): {team_name}\n")

            # Sort players by ADP (ascending order means best available first)
            adp_data_sorted = adp_data.sort_values(by="AVG", ascending=True)

            # Iterate through sorted players to find the best available pick
            for _, player in adp_data_sorted.iterrows():
                if player["Player"] not in selected_players:
                    teams[team_name].append((round_number, player["Player"]))
                    selected_players.add(player["Player"])
                    logging.info(f"{team_name} drafted {player['Player']} in Round {round_number}, Pick {i + 1}\n")
                    break

        # Grade each team's draft based on ADP
        team_grades = {}
        for team, players in teams.items():
            player_names = [player[1] for player in players]
            drafted_players_adp = adp_data[adp_data["Player"].isin(player_names)]
            grade = self.grade_draft_based_on_adp(drafted_players_adp, player_names)
            team_grades[team] = {"grade": round(float(grade), 1)}

            # Sort the teams by grade
            team_grades = dict(sorted(team_grades.items(), key=lambda item: item[1]["grade"], reverse=True))

            # Display players one by one with a line between each
            logging.info(f"Team: {team}")
            for player in players:
                logging.info(f"Round {player[0]}: {player[1]}")

            logging.info(f"Grade: {team_grades[team]['grade']}\n") # Display the grade

        return team_grades

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
    base_url = "https://www.fantasypros.com/nfl/adp/overall.php?"

    # Create an instance of the parser
    parser = DraftCalculator(base_url)

    # parser.parse_all_positions()
    years = list(range(2020, 2026))
    for year in years:
        logging.info(f"Parsing ADP data for year: {year}")
        parser.parse_all_positions(year)
        print(f"ADP data for year {year} parsed successfully.\n")

    # adp_data = pd.read_csv("data/adp_data/adp_rankings_RB.csv")
    # print(adp_data.head(30))

    # Create mock draft options
    # try:
    #     logging.info("------------------ Draft Options ------------------\n")
    #     # Create mock draft options for the given pick number
    #     # mock_draft_options = parser.create_mock_draft_options(adp_data,2)
    #     # for i, player in enumerate(mock_draft_options):
    #     #     logging.info(f"Round {i + 1}: {player}")

    #     # Simulate Draft with ADP data
    #     full_draft_grades = parser.simulate_snake_draft(adp_data)
    #     for team, grade in full_draft_grades.items():
    #         logging.info(f"{team}: {grade}")

    #     # logging.info(f"Mock draft options: {mock_draft_options}\n")
    # except Exception as e:
    #     logging.error(f"Mock draft options failed: {e}")
    #     mock_draft_options = None
