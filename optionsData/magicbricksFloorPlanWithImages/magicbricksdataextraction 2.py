import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Selenium WebDriver
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Read URLs and XIDs from CSV file
input_csv = 'input_urls.csv'  # Replace with the actual input CSV file path
urls = []
xids = []

with open(input_csv, mode="r", newline="", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row if present
    for row in reader:
        if row:  # Skip empty rows
            xids.append(row[0])  # Assuming XID is in the first column
            urls.append(row[1])  # Assuming URL is in the second column

# Prepare output CSV file
output_csv = "floor_p.csv"  # The file where extracted floor plans will be saved

# Open the CSV file once in write mode and add headers
with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["XID", "Unit Type", "Unit Size", "Area Type", "Price", "Possession Date"])

# Iterate over each URL and XID from the CSV
for xid, url in zip(xids, urls):
    floor_plans = []
    print(f"Opening URL: {url}")
    driver.get(url)

    try:
        # Wait until the floor plan container is visible
        floor_plan_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pdp__florpripln__cards"))
        )

        # Find all floor plan cards inside the container
        floor_plan_cards = floor_plan_container.find_elements(By.CSS_SELECTOR, ".swiper-slide")

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

                # Write each floor plan element immediately after extraction
                with open(output_csv, mode="a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", area_type or "Area Not Available", price or "Price Not Available", possession_date or "Possession Not Available"])

            except Exception as e:
                print(f"Skipping a card due to error: {e}")

            # Click the next button after every 2 records
            if (index + 1) % 2 == 0:
                try:
                    next_button = driver.find_element(By.ID, "fp-arrow-next")
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)  # Wait for the next set of floor plans to load
                except:
                    print("Next button not found or could not be clicked.")
                    break

    except Exception as e:
        print(f"Error finding floor plan container: {e}")

# Finish processing
print(f"Floor plan extraction complete. Results saved in {output_csv}")

driver.quit()

# import time
# import csv
# import os
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Helper function to sanitize filenames
# def sanitize_filename(name):
#     return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)

# # Setup Selenium WebDriver
# options = Options()
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

# # Initialize WebDriver
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=options)

# # Read URLs and XIDs from CSV file
# input_csv = 'input_urls.csv'  # Replace with the actual input CSV file path
# urls = []
# xids = []

# with open(input_csv, mode="r", newline="", encoding="utf-8") as file:
#     reader = csv.reader(file)
#     next(reader)  # Skip header row if present
#     for row in reader:
#         if row:  # Skip empty rows
#             xids.append(row[0])  # Assuming XID is in the first column
#             urls.append(row[1])  # Assuming URL is in the second column

# # Prepare output CSV file
# output_csv = "floor_p.csv"
# with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
#     writer = csv.writer(file)
#     writer.writerow(["XID", "Unit Type", "Unit Size", "Area Type", "Price", "Possession Date"])

# # Iterate over each URL and XID from the CSV
# for xid, url in zip(xids, urls):
#     floor_plans = []
#     print(f"Opening URL: {url}")
#     driver.get(url)

#     try:
#         floor_plan_container = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "pdp__florpripln__cards"))
#         )
#         floor_plan_cards = floor_plan_container.find_elements(By.CSS_SELECTOR, ".swiper-slide")

#         for index, card in enumerate(floor_plan_cards):
#             try:
#                 unit_details = card.find_elements(By.CSS_SELECTOR, "div.pdp__florpripln--bhk span")
#                 unit_size = unit_details[0].text.strip() if len(unit_details) > 0 else None
#                 unit_type = unit_details[1].text.strip() if len(unit_details) > 1 else None

#                 try:
#                     area_type = card.find_element(By.CLASS_NAME, "pdp__florpripln--superArea").text.strip()
#                 except:
#                     area_type = None

#                 try:
#                     price = card.find_element(By.CLASS_NAME, "fullPrice__amount").text.strip()
#                 except:
#                     price = None

#                 try:
#                     possession_date = card.find_element(By.CLASS_NAME, "pdp__florpripln--possDate").text.strip()
#                 except:
#                     possession_date = None

#                 if any([unit_size, unit_type, area_type, price, possession_date]):
#                     floor_plans.append([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", area_type or "Area Not Available", price or "Price Not Available", possession_date or "Possession Not Available"])

#                 with open(output_csv, mode="a", newline="", encoding="utf-8") as file:
#                     writer = csv.writer(file)
#                     writer.writerow([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", area_type or "Area Not Available", price or "Price Not Available", possession_date or "Possession Not Available"])

#                 # ---------- Handle image download ONLY for first card ----------
#                 if index == 0:
#                     try:
#                         img_box = card.find_element(By.CLASS_NAME, "pdp__florpripln__imgBox")
#                         driver.execute_script("arguments[0].click();", img_box)

#                         filters_container = WebDriverWait(driver, 10).until(
#                             EC.presence_of_element_located((By.CLASS_NAME, "pdp__unitplan--filters"))
#                         )
#                         filter_items = filters_container.find_elements(By.CLASS_NAME, "pdp__unitplan--item")

#                         cnt = 1
#                         for item in filter_items:
#                             try:
#                                 driver.execute_script("arguments[0].click();", item)
#                                 time.sleep(2)

#                                 img_elem = WebDriverWait(driver, 10).until(
#                                     EC.presence_of_element_located((By.CSS_SELECTOR, "img.pdp__unitplan__image.customLazy"))
#                                 )
#                                 img_url = img_elem.get_attribute("src")

#                                 if img_url:
#                                     filename = f"{sanitize_filename(xid)}_floorplan_{sanitize_filename(unit_type or 'Type')}_{sanitize_filename(area_type or 'Area')}_{cnt}.jpg"
#                                     response = requests.get(img_url)
#                                     if response.status_code == 200:
#                                         with open(filename, "wb") as f:
#                                             f.write(response.content)
#                                         print(f"Saved image: {filename}")
#                                     cnt += 1
#                             except Exception as e:
#                                 print(f"Error processing image filter")
#                     except Exception as e:
#                         print(f"Error in image section")
#                 # -------------------------------------------------------------------

#             except Exception as e:
#                 print(f"Skipping a card due to error: {e}")

#             if (index + 1) % 2 == 0:
#                 try:
#                     next_button = driver.find_element(By.ID, "fp-arrow-next")
#                     driver.execute_script("arguments[0].click();", next_button)
#                     time.sleep(2)
#                 except:
#                     print("Next button not found or could not be clicked.")
#                     break

#     except Exception as e:
#         print(f"Error finding floor plan container")

# print(f"Floor plan extraction complete. Results saved in {output_csv}")
# driver.quit()
