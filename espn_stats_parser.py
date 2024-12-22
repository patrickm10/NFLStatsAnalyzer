from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

def get_espn_stats():
    url = "https://fantasy.espn.com/football/leaders?lineupSlot=2&scoringPeriodId=16&statSplit=singleScoringPeriod"
    driver = webdriver.Chrome()  # Make sure ChromeDriver is installed
    driver.get(url)
    driver.get_log('driver')
    # driver.implicitly_wait(10)  # Wait for page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    table = soup.find('table')
    if table:
        df = pd.read_html(str(table))[0]
        return df
    else:
        return "No tables found"

espn_stats = get_espn_stats()
print(espn_stats)
