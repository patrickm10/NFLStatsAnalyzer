import os
import time
import requests
import csv
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

    try:
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
            return False

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
            return False

    except Exception as e:
        print(f"Error while processing {player_name}: {e}")
        return False

    finally:
        # Close the WebDriver
        driver.quit()

    return True

def process_roster(csv_file, start_line=0):
    no_names = []

    try:
        with open(csv_file, newline='', encoding='utf-8', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile)

            for line_number, row in enumerate(reader, start=1):  # Line numbers start at 1
                if line_number < start_line:
                    continue  # Skip lines before the start line

                player_name = row['Name']
                print(f"Processing {player_name} (Line {line_number})...")

                try:
                    success = save_player_headshot(player_name)
                    if not success:
                        no_names.append(player_name)
                except Exception as e:
                    print(f"Unexpected error for {player_name}: {e}")
                    no_names.append(player_name)

    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return

    # Save the names with no headshot to a text file
    if no_names:
        with open('no_names.txt', 'a', encoding='utf-8') as f:  # Append to the file to avoid overwriting
            for name in no_names:
                f.write(name + '\n')
        print(f"Names with no headshot saved to 'no_names.txt'.")

# Run the process starting from line 808
process_roster('nfl_roster.csv', start_line=0)#adjust if script stops halfway through
