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
        df["Player"] = df["Player Team (Bye)"].apply(self.remove_team_from_name)

        df.to_csv(filename, index=False)
        logging.info(f"df: {df}")
        logging.info(f"Saved data to {filename}")
    
    def grade_draft_based_on_adp(self, adp_data, draft_picks):
        """Grades a draft based on ADP data.
        Args:
            adp_data (DataFrame): DataFrame containing ADP data.
            draft_picks (list): List of player names drafted.
            Returns:
            str: Draft grade.
        """
        # Filter the ADP data for the drafted players
        drafted_players = adp_data[adp_data["Player"].isin(draft_picks)]

        # Ensure 'Pick' column exists
        if 'Sleeper' not in drafted_players.columns:
            logging.error("'Sleeper' column is missing from the ADP data.")
            return None

        # Calculate the difference between ADP and draft position
        drafted_players["Diff"] = drafted_players["AVG"] - drafted_players["Sleeper"]

        # Calculate the total difference
        total_diff = drafted_players["Diff"].sum()

        # Calculate the total number of players drafted
        total_players = len(draft_picks)

        # Calculate the average difference
        avg_diff = total_diff / total_players

        # Grade the draft based on the average difference on a scale of 100
        grade = 100 + avg_diff * 10  # Adjust the scale as needed

        # Ensure the grade is within 0 to 100
        grade = max(0, min(100, grade))

        return grade

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

    # Grade a test draft
    try:
        adp_data = pd.read_csv("adp_rankings_RB.csv")
        draft_picks = [
        {"Pick": 1, "Player": "Christian McCaffrey"},
        {"Pick": 2, "Player": "Dalvin Cook"},
        {"Pick": 3, "Player": "Alvin Kamara"},
        {"Pick": 4, "Player": "Derrick Henry"}
    ]
        grade = parser.grade_draft_based_on_adp(adp_data, draft_picks)
    except Exception as e:
        logging.error(f"Draft grading failed: {e}")
        grade = None

    # Print the draft grade
    logging.info(f"Draft grade: {grade}\n")

