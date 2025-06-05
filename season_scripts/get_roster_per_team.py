# Date Last Edited: 4/9/25
# Authors: Matthew Fredo & Patrick Mejia
#
# Functionality:
# *Run first to update the team rosters for all teams
#
# This script runs through all NFL teams from NFL.com and creates a csv of their current skill
# player roster
#
# Saved to (e.g., "rosters/buffalo-bills.csv")
#

import requests
from bs4 import BeautifulSoup
import csv
import os


# List of all NFL team names and their abbreviations
team_abbreviations = {
    "buffalo-bills": "BUF",
    "miami-dolphins": "MIA",
    "new-england-patriots": "NE",
    "new-york-jets": "NYJ",
    "baltimore-ravens": "BAL",
    "cincinnati-bengals": "CIN",
    "cleveland-browns": "CLE",
    "pittsburgh-steelers": "PIT",
    "houston-texans": "HOU",
    "indianapolis-colts": "IND",
    "jacksonville-jaguars": "JAX",
    "tennessee-titans": "TEN",
    "denver-broncos": "DEN",
    "kansas-city-chiefs": "KC",
    "las-vegas-raiders": "LV",
    "los-angeles-chargers": "LAC",
    "chicago-bears": "CHI",
    "detroit-lions": "DET",
    "green-bay-packers": "GB",
    "minnesota-vikings": "MIN",
    "atlanta-falcons": "ATL",
    "carolina-panthers": "CAR",
    "new-orleans-saints": "NO",
    "tampa-bay-buccaneers": "TB",
    "dallas-cowboys": "DAL",
    "new-york-giants": "NYG",
    "philadelphia-eagles": "PHI",
    "washington-commanders": "WAS",
    "arizona-cardinals": "ARI",
    "los-angeles-rams": "LAR",
    "san-francisco-49ers": "SF",
    "seattle-seahawks": "SEA",
}

# Create the 'rosters' folder if it doesn't exist
os.makedirs("rosters", exist_ok=True)

valid_positions = {"QB", "WR", "RB", "TE", "K"}
valid_statuses = {"ACT", "RES", "PUP", "NFI", "TRC", "UDF"}

for team, abbreviation in team_abbreviations.items():
    url = f"https://www.nfl.com/teams/{team}/roster"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    players_table = soup.find("table", class_="d3-o-table")

    player_data = []
    rows = players_table.find_all("tr")[1:] if players_table else []

    for row in rows:
        columns = row.find_all("td")
        if len(columns) > 1:
            player_name = columns[0].text.strip()
            number = columns[1].text.strip()
            position = columns[2].text.strip()
            status = columns[3].text.strip()
            height = columns[4].text.strip()
            weight = columns[5].text.strip()
            experience = (
                "1" if columns[6].text.strip() == "R" else columns[6].text.strip()
            )
            college = columns[7].text.strip()

            if status in valid_statuses and position in valid_positions:
                player_data.append(
                    [
                        player_name,
                        number,
                        position,
                        status,
                        height,
                        weight,
                        experience,
                        college,
                        abbreviation,
                    ]
                )

    csv_file = f"rosters/{team}.csv"
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Player",
                "Number",
                "Position",
                "Status",
                "Height",
                "Weight",
                "Experience",
                "College",
                "Team",
            ]
        )
        writer.writerows(player_data)

    print(f"Data for {team.replace('-', ' ').title()} saved to {csv_file}")

# Combine all team CSVs into one master CSV
combined_csv = "rosters/fullNFLSkillRoster.csv"
with open(combined_csv, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(
        [
            "Player",
            "Number",
            "Position",
            "Status",
            "Height",
            "Weight",
            "Experience",
            "College",
            "Team",
        ]
    )

    for team in team_abbreviations.keys():
        csv_file = f"rosters/{team}.csv"
        if os.path.exists(csv_file):
            with open(csv_file, mode="r", newline="") as team_file:
                reader = csv.reader(team_file)
                next(reader)  # Skip header
                writer.writerows(reader)

print(f"Combined roster saved to {combined_csv}")
