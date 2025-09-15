import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import os
 
# Setup Selenium WebDriver
options = Options()
#options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
 
# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
 
# Read input CSV (Skipping first row)
input_file = "input_urls.csv"
output_file = "magicbricks.csv"
floor_plans_csv = "floor_p.csv" 
# Read CSV using pandas
df = pd.read_csv(input_file, skiprows=1, header=None)  # Skip first row
xids = df[0].tolist()  # Extract XIDs from the first column
urls = df[1].tolist()  # Extract URLs from the fourth column
 
# Filter URLs that contain 'pdpid' with other text before and after
filtered_urls = []
filtered_xids = []
for xid, url in zip(xids, urls):
    if 'pdpid' in url:
        filtered_urls.append(url)
        filtered_xids.append(xid)
 
urls = filtered_urls
xids = filtered_xids
 
# Work on top 20 records
# urls = urls[3256:]
# xids = xids[3256:]
# xids=["r145369"]
# urls=["https://www.magicbricks.com/173-west-oaks-wakad-pune-pdpid-4d4235323037383531"]# Prepare output data list
data_list = []

 
# Iterate over each URL
for xid, url in zip(xids, urls):
    floor_plans = []
    print(f"Opening URL: {url}")
    driver.get(url)
    time.sleep(3)  # Wait for elements to load
 
    # Extracting data

    try:
        

# Locate the main container with class 'pdp__florpripln__cards'
        try:
            floor_plan_container = driver.find_element(By.CLASS_NAME, "pdp__florpripln__cards")
            
            # Find all floor plan cards inside the container
            floor_plan_cards = floor_plan_container.find_elements(By.CSS_SELECTOR, ".swiper-slide, .swiper-slide swiper-slide-next , .swiper-slide swiper-slide-prev, .swiper-slide swiper-slide-active")
            # Take the first card only
            # Create a folder named 'floor plans' in the current working directory
            output_folder = os.path.join(os.getcwd(), "floor plans")
            os.makedirs(output_folder, exist_ok=True)

            if floor_plan_cards:
                first_card = floor_plan_cards[0]
                try:
                    # Click the element with class 'pdp__florpripln__imgBox' through JS
                    img_box = first_card.find_element(By.CLASS_NAME, "pdp__florpripln__imgBox")
                    driver.execute_script("arguments[0].click();", img_box)
                    time.sleep(2)  # Wait for the new content to load

                    # Find the element with class 'pdp__unitplan--filters'
                    filters_div = driver.find_element(By.CLASS_NAME, "pdp__unitplan--filters")
                    filter_items = filters_div.find_elements(By.CLASS_NAME, "pdp__unitplan--item")

                    # Click every element in the filters div
                    for filter_item in filter_items:
                        try:
                            driver.execute_script("arguments[0].click();", filter_item)
                            time.sleep(2)  # Wait for the image to load

                            # Find the image with class 'pdp__unitplan__image customLazy'
                            try:
                                image = driver.find_element(By.CSS_SELECTOR, "img.pdp__unitplan__image.customLazy")
                                image_url = image.get_attribute("src")

                                # Download and save the image
                                if image_url:
                                    response = requests.get(image_url, stream=True)
                                    if response.status_code == 200:
                                        config_area = filter_item.text.replace(" ", "_").replace("/", "_")
                                        image_filename = os.path.join(output_folder, f"{xid}_floorplan_{config_area}.jpg")
                                        with open(image_filename, "wb") as img_file:
                                            for chunk in response.iter_content(1024):
                                                img_file.write(chunk)
                                        print(f"Image saved as {image_filename}")
                                    else:
                                        print(f"Failed to download image from {image_url}")
                            except Exception as e:
                                print(f"Error finding or downloading image")

                        except Exception as e:
                            print(f"Error clicking filter item")

                except Exception as e:
                    print(f"Error interacting with the first card")
            for index, card in enumerate(floor_plan_cards):
                try:
                    # Extract unit size and type
                    unit_details = card.find_elements(By.CSS_SELECTOR, "div.pdp__florpripln--bhk span")
                    unit_size = unit_details[0].text.strip() if len(unit_details) > 0 else None
                    unit_type = unit_details[1].text.strip() if len(unit_details) > 1 else None

                    # Extract area type
                    try:
                        area_type = card.find_element(By.CLASS_NAME, "pdp__florpripln--superArea").text.strip()
                    except:
                        area_type = None

                    # Extract price
                    try:
                        price = card.find_element(By.CLASS_NAME, "fullPrice__amount").text.strip()
                    except:
                        price = None

                    # Extract possession date
                    try:
                        possession_date = card.find_element(By.CLASS_NAME, "pdp__florpripln--possDate").text.strip()
                    except:
                        possession_date = None

                    # Only append if at least one of the key details is present
                    if any([unit_size, unit_type, area_type, price, possession_date]):
                        floor_plans.append([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", area_type or "Area Not Available", price or "Price Not Available", possession_date or "Possession Not Available"])

                except Exception as e:
                    print(f"Skipping a card due to error")

                # Click the next button after every 2 records
                if (index + 1) % 2 == 0:
                    try:
                        next_button = driver.find_element(By.ID, "fp-arrow-next")
                        driver.execute_script("arguments[0].click();", next_button)
                        time.sleep(2)  # Wait for the next set of floor plans to load
                    except:
                        print("Next button not found or could not be clicked.")
                        break

        except:
            print("No floor plan container found on this page.")


        # Print extracted floor plans for debugging
        for plan in floor_plans:
            print(plan)

    except Exception as e:
        print(f"Error extracting floor plans")

    # Save to CSV simultaneously
    

    with open(floor_plans_csv, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Check if file is empty to write header
            writer.writerow(["XID", "Unit Type", "Unit Size", "Area Type", "Price", "Possession Date"])
        # Write data
        writer.writerows(floor_plans)
        print(f"Data appended to {floor_plans_csv}")

print(f" Data extraction complete. Results appended in {output_file}")

driver.quit()
 
