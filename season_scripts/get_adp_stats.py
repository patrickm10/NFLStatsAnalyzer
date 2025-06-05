# FantasyPros ADP Stats Parser
# This script fetches the ADP stats from FantasyPros and saves them by position and year.
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
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
        }

    def fetch_data(self, position, year):
        """Fetch the HTML page content for a given position and year."""
        url = f"{self.base_url}{position.lower()}.php?year={year}"
        logging.info(f"Fetching data from: {url}")

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logging.error(f"Failed to fetch data: {response.status_code}")
                return None
            return response.text
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None

    def parse_data(self, html_content):
        """Parse HTML content and extract table headers and rows."""
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")
        if not table:
            logging.warning("No table found in the page content.")
            return [], []

        headers = [th.get_text().strip() for th in table.find_all("th")]
        rows = table.find_all("tr")[1:]  # Skip header row
        data = [[td.get_text().strip() for td in row.find_all("td")] for row in rows]

        logging.info(f"Testing Rows:  {data[:3]}")
        return headers, data

    def parse_position(self, position, year):
        """Fetch and parse data for a given position and year."""
        html_content = self.fetch_data(position, year)
        if not html_content:
            return [], []
        return self.parse_data(html_content)

    def parse_all_positions(self, year):
        """Parse all positions (QB, RB, WR, TE) for a specific year and save each split by POS."""
        positions = ["QB", "RB", "WR", "TE"]
        for position in positions:
            headers, data = self.parse_position(position, year)
            if headers and data:
                filename = f"data/adp_data/{year}/{position}.csv"
                self.save_to_csv(headers, data, filename, split_by_position=True)
            else:
                logging.warning(f"No data found for {position} in {year}")

    def save_to_csv(self, headers, data, filename, split_by_position=False):
        """Save data to CSV. Optionally split into multiple files based on POS (WR, RB, etc.)."""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df = pd.DataFrame(data, columns=headers)

        if "POS" in df.columns:
            df["Main_POS"] = df["POS"].str.extract(r'^([A-Z]+)')

        if split_by_position and "Main_POS" in df.columns:
            for pos, group_df in df.groupby("Main_POS"):
                pos_filename = filename.replace(".csv", f"_{pos}.csv")
                group_df.drop(columns=["Main_POS"], inplace=True)
                group_df.to_csv(pos_filename, index=False)
                logging.info(f"Saved {len(group_df)} {pos} players to {pos_filename}")
        else:
            df.to_csv(filename, index=False)
            logging.info(f"Saved {len(df)} players to {filename}")

    def run(self, position, output_file, year):
        """Run a single-position scrape and save."""
        headers, data = self.parse_position(position, year)
        if headers and data:
            self.save_to_csv(headers, data, output_file)
        else:
            logging.warning(f"No data found for {position} in {year}")


if __name__ == "__main__":
    # Main script entry point
    base_url = "https://www.fantasypros.com/nfl/adp/"
    parser = DraftCalculator(base_url)

    years = list(range(2020, 2026))  # 2020 through 2025
    for year in years:
        logging.info(f"--- Parsing ADP data for year: {year} ---")
        parser.parse_all_positions(year)
        print(f"ADP data for year {year} parsed successfully.\n")
