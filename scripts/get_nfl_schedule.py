from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import warnings
import pandas as pd

# Suppress all warnings (like ResourceWarnings or Selenium deprecation warnings)
warnings.filterwarnings("ignore")

def scrape_game_location(driver, game_url):
    driver.get(game_url)
    try:
        # Wait until a div with a class containing 'r-color-zyhucb' is present (likely location)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='r-color-zyhucb']"))
        )
        html = driver.page_source
    except Exception as e:
        print(f"Failed to load game page {game_url} or find location:", e)
        return None

    soup = BeautifulSoup(html, "html.parser")
    venue_div = soup.select_one("div[class*='r-color-zyhucb']")
    if venue_div:
        return venue_div.text.strip()
    else:
        return None

def scrape_nfl_matchups(url: str):
    options = Options()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "nfl-c-matchup-strip__left-area"))
        )
        html = driver.page_source
    except Exception as e:
        print("Timed out waiting for matchup containers to load:", e)
        driver.quit()
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    matchup_links = soup.find_all("a", class_="nfl-c-matchup-strip__left-area")

    if not matchup_links:
        print("No matchup containers found.")
        driver.quit()
        return []

    matchups = []

    for matchup_link in matchup_links:
        game_div = matchup_link.find("div", class_="nfl-c-matchup-strip__game")
        if not game_div:
            continue

        teams = []
        for team_div in game_div.find_all("div", class_="nfl-c-matchup-strip__team"):
            abbr_elem = team_div.find("span", class_="nfl-c-matchup-strip__team-abbreviation")
            name_elem = team_div.find("span", class_="nfl-c-matchup-strip__team-fullname")

            abbr = abbr_elem.text.strip() if abbr_elem else None
            name = name_elem.text.strip() if name_elem else None

            teams.append({
                "abbreviation": abbr,
                "fullname": name,
            })

        game_info_div = matchup_link.find("div", class_="nfl-c-matchup-strip__game-info")
        time_info = None
        if game_info_div:
            date_time_span = game_info_div.find("span", class_="nfl-c-matchup-strip__date-time")
            timezone_span = game_info_div.find("span", class_="nfl-c-matchup-strip__date-timezone")
            if date_time_span and timezone_span:
                time_info = f"{date_time_span.text.strip()} {timezone_span.text.strip()}"

        game_href = matchup_link["href"]
        game_url = f"https://www.nfl.com{game_href}"

        # Scrape location from game detail page using partial class matching
        location = scrape_game_location(driver, game_url)

        matchups.append({
            "teams": teams,
            "time": time_info,
            "location": location,
        })

    driver.quit()
    return matchups


if __name__ == "__main__":
    year = 2025
    all_games = []
    for week in range(1, 19):
        print(f"--- Week {week} ---")
        url = f"https://www.nfl.com/schedules/{year}/REG{week}/"
        matchups = scrape_nfl_matchups(url)

        for idx, m in enumerate(matchups, 1):
            for team in m["teams"]:
                all_games.append({
                    "week": week,
                    "game_number": idx,
                    "team_abbreviation": team["abbreviation"],
                    "team_fullname": team["fullname"],
                    "time": m["time"],
                    "location": m["location"]
                })
            print(f"Game {idx}: Time - {m['time']} - Location - {m['location']}")
            for team in m["teams"]:
                print(f"  {team['abbreviation']} - {team['fullname']}")
            print("-" * 40)
        print(f"Total games found for week {week}: {len(matchups)}\n")
    print("Total games found across all weeks:", len(all_games)//2)

    # Save to CSV
    df = pd.DataFrame(all_games)
    df.to_csv("nfl_schedule_2025.csv", index=False)
    print("Saved all games to nfl_schedule_2025.csv")
