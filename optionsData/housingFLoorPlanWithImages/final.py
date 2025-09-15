import csv
import time
import os
import re
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from urllib3.exceptions import ReadTimeoutError
from webdriver_manager.chrome import ChromeDriverManager

# Create folder if it doesn't exist
output_dir = os.path.join(os.getcwd(), "floor plans2")
os.makedirs(output_dir, exist_ok=True)

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|\n\r]+', '_', name)  # Replace illegal characters
    return name.strip()

# Function to restart the driver
def restart_driver():
    global driver
    print("Restarting the driver...")
    driver.quit()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Set up Selenium WebDriver
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# File names
input_file = 'outputUrls2.csv'
output_file = 'HousingOptionsData2.csv'

# Read input CSV
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    # Open output CSV in append mode ('a') and write header if needed
    with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv)
        if outcsv.tell() == 0:  # Check if the file is empty
            writer.writerow(['XID', 'Configuration', 'List Item', 'Price', 'Area'])  # Write headers only if file is empty

    # Main loop for processing rows
    for row in reader:
        xid = row.get('XID', '').strip()
        link = row.get('Housing.com Link', '').strip()

        print("Processing XID:", xid, "Link:", link)

        if link.startswith('https://housing.com'):
            try:
                # Close all tabs except the current one
                for handle in driver.window_handles[:-1]:
                    driver.switch_to.window(handle)
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])

                driver.get(link)
                time.sleep(5)  # Wait for the page to settle

                # Click the 'Ok, Got it' button if it appears
                try:
                    ok_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
                    )
                    driver.execute_script("arguments[0].click();", ok_button)
                    print("Clicked 'Ok, Got it' button.")
                except:
                    print("No 'Ok, Got it' button found or already dismissed.")

                # Wait for page load
                try:
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                except:
                    print(f"Page load timeout for {link}")
                    continue  # Skip this entry

                try:
                    floorPlanBtn = driver.find_element(By.LINK_TEXT, "Floor Plan")
                    driver.execute_script("arguments[0].click();", floorPlanBtn)
                    print("Clicked 'Floor Plan' button.")
                except:
                    print("No 'Floor Plan' button found.")

                try:
                    first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")
                    first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
                    print(f"Found {len(first_list_items)} items in the first list.")

                    for item in first_list_items:
                        driver.execute_script("arguments[0].click();", item)
                        time.sleep(1)
                        config_item = item.text.strip()
                        print("Clicked an item in the first list.")

                        previous_data = set()
                        while True:
                            try:
                                nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
                                nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
                                print(f"Found {len(nested_list_items)} items in the nested list.")

                                current_data = set()
                                for sub_item in nested_list_items:
                                    list_item_text = sub_item.text.strip()
                                    current_data.add(list_item_text)
                                    driver.execute_script("arguments[0].click();", sub_item)
                                    time.sleep(1)
                                    print(f"Clicked an item in the nested list: {list_item_text}")

                                    # Extract price
                                    try:
                                        price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
                                        driver.execute_script("arguments[0].scrollIntoView();", price_element)
                                        time.sleep(1)  # Wait for scroll to settle
                                        price_text = price_element.text.strip()
                                    except:
                                        price_text = "Price not found"

                                    # Click 2D button and download image
                                    try:
                                        # Click the 2D button
                                        two_d_button = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[2]/div/span[2]')
                                        driver.execute_script("arguments[0].click();", two_d_button)
                                        print("Clicked 2D floor plan button.")
                                        time.sleep(2)
                                    except:
                                        print("2D button not found or already clicked.")

                                    try:
                                        # Wait for image to appear
                                        img_elem = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/img')
                                        img_url = img_elem.get_attribute("src")
                                        print(f"Image URL: {img_url}")

                                        # Download the image
                                        response = requests.get(img_url, timeout=15)
                                        response.raise_for_status()

                                        filename = sanitize_filename(f"{xid}_2dfloorplan_{config_item}_{list_item_text}.jpg")
                                        filepath = os.path.join(output_dir, filename)

                                        with open(filepath, "wb") as f:
                                            f.write(response.content)

                                        print(f"Saved floor plan image: {filepath}")

                                        try:
                                            info_labels = driver.find_elements(By.CLASS_NAME, "css-1kuy7z7")
                                            info_values = driver.find_elements(By.CLASS_NAME, "css-2yrfz4")

                                            if info_labels and info_values:
                                                carpet_area_label = info_labels[0].text.strip()
                                                carpet_area_value = info_values[0].text.strip()
                                                carpet_area_text = f"{carpet_area_label}: {carpet_area_value}"
                                                print(f"Extracted carpet area: {carpet_area_text}")
# current_data["Area"] = carpet_area_text
                                            else:
                                                print("Carpet area info not found.")
                                        except Exception as e:
                                            print(f"Could not extract carpet area")
                                            carpet_area_text = "N/A"

                                    except Exception as e:
                                        print(f"Could not retrieve or save floor plan image: {e}")

                                    # Write to CSV
                                    with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
                                        writer = csv.writer(outcsv)
                                        writer.writerow([xid, config_item, list_item_text, price_text, carpet_area_text])
                                        outcsv.flush()

                                if current_data == previous_data:
                                    print("No new data found. Ending pagination.")
                                    break
                                previous_data = current_data

                            except StaleElementReferenceException:
                                print("Stale element encountered. Retrying...")
                                continue
                            except:
                                print("No nested list found under this item.")
                                break

                            # Pagination - Next button
                            try:
                                next_button = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
                                next_button_class = next_button.get_attribute("class")
                                if "css-hskvoc" in next_button_class:
                                    print("Next button is disabled. Ending pagination.")
                                    break
                                driver.execute_script("arguments[0].click();", next_button)
                                time.sleep(2)
                                print("Clicked 'Next' button.")
                            except:
                                print("No 'Next' button found or page did not change. Ending pagination.")
                                break

                except Exception as e:
                    print(f"Error finding lists")

            except ReadTimeoutError as e:
                print(f"ReadTimeoutError encountered: {e}")
                restart_driver()  # Restart the driver
                print(f"Retrying URL: {link}")
                driver.get(link)  # Reload the same URL and continue processing
                time.sleep(5)  # Wait for the page to settle

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                continue  # Skip to the next row if an error occurs

print(f"Data extraction complete. Output saved to {output_file}")
driver.quit()
