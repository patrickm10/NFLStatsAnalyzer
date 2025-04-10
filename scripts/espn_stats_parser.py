from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_espn_stats(position_id):
    url = f"https://fantasy.espn.com/football/leaders?lineupSlot={position_id}&scoringPeriodId=0&statSplit=currSeason"
    
    try:
        driver = webdriver.Chrome()
        driver.get(url)

        # Ensure table data loads properly
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
    # Extract table
    table = soup.find('table')
    if not table:
        print("No tables found on the page")
        return None

    # Extract data from table rows
    rows = table.find_all('tr')
    data = [[col.get_text(strip=True) for col in row.find_all(['th', 'td'])] for row in rows]

    # Use the first row as headers
    headers = data[0]
    headers.append('Team')

    # Extract data starting from the second row
    data = data[1:]
    for row in data:
        player_name = row[0]
        team = player_name[-5:-2]
        row.append(team)

    # Debugging: Print all rows
    for i, row in enumerate(data):
        print(f"Row {i}: {row}")

    # Handle mismatched rows
    if data:
        header = data[0]
        filtered_data = [row for row in data[1:] if len(row) == len(header)]
        df = pd.DataFrame(filtered_data, columns=header)
        return df
    else:
        print("No data found in table")
        return None

if __name__ == "__main__":
    # Scrape and save stats for QB, RB, WR
    positions = {"RB": 2, "WR": 4}
    
    for pos, pos_id in positions.items():
        df = scrape_espn_stats(pos_id)
        
        if df is not None:
            print(f"\n{pos} Stats:\n", df.head())
            df.to_csv(f"{pos.lower()}_stats.csv", index=False)
            print(f"{pos} stats saved to {pos.lower()}_stats.csv")
        else:
            print(f"Failed to retrieve {pos} stats")
