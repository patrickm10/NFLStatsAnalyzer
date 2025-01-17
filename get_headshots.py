import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def save_player_headshot(player_name):
    # Create the 'headshots' folder if it doesn't exist
    folder_path = 'headshots'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Set up Selenium WebDriver (Chrome in this case)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Construct the player's page URL
    url = f'https://www.nfl.com/players/{player_name.lower().replace(" ", "-")}/'

    # Open the player's page
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    # Find the headshot image element
    try:
        img_element = driver.find_element(By.XPATH, '//img[contains(@src, "player_profile_landscape")]')
        img_url = img_element.get_attribute('src')
    except Exception as e:
        print(f"Failed to find headshot image for {player_name}: {e}")
        driver.quit()
        return

    # Download the image
    img_response = requests.get(img_url)
    if img_response.status_code == 200:
        # Save the image as PNG
        img_path = os.path.join(folder_path, f'{player_name.replace(" ", "_")}_headshot.png')
        with open(img_path, 'wb') as f:
            f.write(img_response.content)
        print(f"Image saved successfully as {img_path}")
    else:
        print(f"Failed to download the image. Status code: {img_response.status_code}")

    # Close the WebDriver
    driver.quit()

# Example: Save Josh Allen's headshot
save_player_headshot("Josh Allen")
