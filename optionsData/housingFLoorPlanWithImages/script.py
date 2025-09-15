# # import csv
# # import time
# # from selenium import webdriver
# # from selenium.webdriver.chrome.service import Service
# # from selenium.webdriver.chrome.options import Options
# # from selenium.webdriver.common.by import By
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as EC
# # from selenium.common.exceptions import StaleElementReferenceException
# # from webdriver_manager.chrome import ChromeDriverManager

# # # Set up Selenium WebDriver
# # options = Options()
# # options.add_argument('--disable-gpu')
# # options.add_argument('--no-sandbox')
# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # # File names
# # input_file = 'noida697.csv'
# # output_file = 'noida697FloorPlanData.csv'

# # # Read input CSV
# # with open(input_file, newline='', encoding='utf-8') as csvfile:
# #     reader = csv.DictReader(csvfile)
    
# #     # Open output CSV in append mode ('a') and write header if needed
# #     with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
# #         writer = csv.writer(outcsv)
# #         if outcsv.tell() == 0:  # Check if the file is empty
# #             writer.writerow(['XID', 'Configuration', 'List Item', 'Price'])  # Write headers only if file is empty

# #     for row in reader:
# #         xid = row.get('XID', '').strip()
# #         link = row.get('Housing.com Link', '').strip()

# #         print("Processing XID:", xid, "Link:", link)

# #         if link.startswith('https://housing.com'):
# #             driver.get(link)
# #             time.sleep(2)  # Wait for the page to settle

# #             # Click the 'Ok, Got it' button if it appears
# #             try:
# #                 ok_button = WebDriverWait(driver, 5).until(
# #                     EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
# #                 )
# #                 driver.execute_script("arguments[0].click();", ok_button)
# #                 print("Clicked 'Ok, Got it' button.")
# #             except:
# #                 print("No 'Ok, Got it' button found or already dismissed.")

# #             # Wait for page load
# #             try:
# #                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
# #             except:
# #                 print(f"Page load timeout for {link}")
# #                 continue  # Skip this entry

# #             extracted_data = []  # Store extracted data

# #             # Find all containers with class "config-header-container css-n0tp0a"
# #             try:
# #                 first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")  # The first one is the main list
# #                 first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
# #                 print(f"Found {len(first_list_items)} items in the first list.")

# #                 for item in first_list_items:
# #                     driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
# #                     time.sleep(1)
# #                     config_item = item.text.strip()  # Get the text of the clicked item
# #                     print("Clicked an item in the first list.")

# #                     previous_data = set()
# #                     while True:
# #                         # Look for a nested list inside THIS item (not globally)
# #                         try:
# #                             nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
# #                             nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
# #                             print(f"Found {len(nested_list_items)} items in the nested list.")

# #                             current_data = set()
# #                             for sub_item in nested_list_items:
# #                                 list_item_text = sub_item.text.strip()  # Get the text of the sub-item
# #                                 current_data.add(list_item_text)
# #                                 driver.execute_script("arguments[0].click();", sub_item)  # Click via JavaScript
# #                                 time.sleep(1)
# #                                 print(f"Clicked an item in the nested list: {list_item_text}")

# #                                 # Extract price from the given XPath
# #                                 try:
# #                                     price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
# #                                     price_text = price_element.text.strip()
# #                                 except:
# #                                     price_text = "Price not found"

# #                                 # Append row immediately to CSV
# #                                 with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
# #                                     writer = csv.writer(outcsv)
# #                                     writer.writerow([xid, config_item ,list_item_text, price_text])
# #                                     outcsv.flush()  # Ensure data is written immediately

# #                             if current_data == previous_data:
# #                                 print("No new data found. Ending pagination.")
# #                                 break
# #                             previous_data = current_data
                        
# #                         except StaleElementReferenceException:
# #                             print("Stale element encountered. Retrying...")
# #                             continue
# #                         except:
# #                             print("No nested list found under this item.")
# #                             break
                        
# #                         # Check for the Next button
# #                         try:
# #                             next_button = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
# #                             next_button_class = next_button.get_attribute("class")
# #                             if "css-hskvoc" in next_button_class:
# #                                 print("Next button is disabled. Ending pagination.")
# #                                 break
# #                             driver.execute_script("arguments[0].click();", next_button)
# #                             time.sleep(2)
# #                             print("Clicked 'Next' button.")
# #                         except:
# #                             print("No 'Next' button found or page did not change. Ending pagination.")
# #                             break
            
# #             except Exception as e:
# #                 print(f"Error finding lists: {e}")

# # print(f"Data extraction complete. Output saved to {output_file}")
# # driver.quit()

# import glob
# import shutil
# def move_and_rename_last_download(download_dir, new_file_name):
#     """
#     Moves the last downloaded file from the default Downloads folder to a specified directory 
#     and renames the file.
    
#     :param download_dir: The target directory to move the file to.
#     :param new_file_name: The new name for the downloaded file.
#     """
#     # Path to the default Downloads directory (Change if needed)
    
#     default_downloads_dir = os.path.join(os.getcwd(), "temp_downloads")  # Creates a temp folder in the script directory
#     if not os.path.exists(default_downloads_dir):
#         os.makedirs(default_downloads_dir)
    
#     # List all files in the Downloads folder sorted by modification time (newest first)
#     downloaded_files = sorted(
#         (f for f in os.listdir(default_downloads_dir) if os.path.isfile(os.path.join(default_downloads_dir, f))),
#         key=lambda f: os.path.getmtime(os.path.join(default_downloads_dir, f)),
#         reverse=True
#     )
    
#     # Ensure there is at least one file
#     if not downloaded_files:
#         print("No files found in the Downloads folder.")
#         return

#     # The last downloaded file
#     last_downloaded_file = downloaded_files[0]
    
#     # Full path of the last downloaded file
#     source_file_path = os.path.join(default_downloads_dir, last_downloaded_file)
    
#     # Check if the file is still downloading (Chrome creates .crdownload files)
#     if last_downloaded_file.endswith(".crdownload"):
#         print("Download still in progress, waiting for completion.")
#         time.sleep(1)
#         return move_and_rename_last_download(download_dir, new_file_name)  # Recurse to check again
    
#     # Target path in the desired directory with the new name
#     target_file_path = os.path.join(download_dir, new_file_name)
    
#     # Check if the file already exists in the download directory
#     if os.path.exists(target_file_path):
#         print(f"File {new_file_name} already exists in {download_dir}. Deleting from temporary and doing nothing.")
#         os.remove(source_file_path)
#     else:
#         # Move and rename the file
#         try:
#             shutil.move(source_file_path, target_file_path)
#             print(f"Moved and renamed file to {target_file_path}")
#         except Exception as e:
#             print(f"Error while moving or renaming the file: {e}")

# def download_and_rename_pdf(driver, project_name, file_type, download_dir):
#     """
#     Triggers file download via Selenium, and renames it dynamically based on project_name.
    
#     :param driver: The Selenium WebDriver instance.
#     :param project_name: The name of the project to use in the filename.
#     :param file_type: The type of the file (e.g., 'GujRERA_Certificate').
#     :param download_dir: Directory where the file is saved.
#     """
#     # Simulate clicking the download button or link to trigger the download
#     try:
#         # Locate the download link or button by XPath (Modify as per the actual page structure)
#         #download_button = driver.find_element(By.XPATH, xpth)
            
#         #download_button.click()
#         wait = WebDriverWait(driver, 10)

#         # Wait until the modal with the class "fade show" is visible and interactable
#         modal = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal fade show')]")))

#         # Wait for the "Download" button within the modal to be clickable
#         download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Download']")))

#         # Optionally, print modal title for confirmation
#         modal_title = modal.find_element(By.XPATH, ".//div[contains(@class, 'modal-header')]//h4").text
#         print(f"Modal Title: {modal_title}")

#         # Click the download button
#         ActionChains(driver).move_to_element(download_button).click().perform()
#         print(f"Downloading {file_type}...")
#         time.sleep(30)
#         download_dir = os.path.join(os.getcwd(), "downloaded_pdfs") # Current directory (can change to your custom directory)
        
#         new_file_name = f"{project_name}_{file_type}.pdf"  # New name for the file

#         move_and_rename_last_download(download_dir, new_file_name)
#         # Wait for the file to download (increase the time if necessary)
       
#         print(f"{file_type} renamed to {new_file_name}")
#         close_button = modal.find_element(By.XPATH, ".//button[@class='close']")
#         close_button.click()
#     except Exception as e:
#         print(f"Error while downloading or renaming {file_type}: {e}")

# import csv
# import time
# import os
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Selenium WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # File names
# input_file = 'input.csv'
# output_file = 'output.csv'

# # Create folder for saving screenshots
# output_image_dir = os.path.join(os.getcwd(), 'floor_plans')
# os.makedirs(output_image_dir, exist_ok=True)
# print("Screenshots will be saved in:", output_image_dir)

# # Read input CSV
# with open(input_file, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     # Open output CSV in append mode ('a') and write header if needed
#     with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#         writer = csv.writer(outcsv)
#         if outcsv.tell() == 0:  # Check if the file is empty
#             writer.writerow(['XID', 'Configuration', 'List Item', 'Price'])  # Write headers only if file is empty

#     for row in reader:
#         xid = row.get('XID', '').strip()
#         link = row.get('Housing.com Link', '').strip()

#         print("Processing XID:", xid, "Link:", link)

#         if link.startswith('https://housing.com'):
#             driver.get(link)
#             time.sleep(2)  # Wait for the page to settle

#             # Click the 'Ok, Got it' button if it appears
#             try:
#                 ok_button = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
#                 )
#                 driver.execute_script("arguments[0].click();", ok_button)
#                 print("Clicked 'Ok, Got it' button.")
#             except:
#                 print("No 'Ok, Got it' button found or already dismissed.")

#             # Wait for page load
#             try:
#                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#             except:
#                 print(f"Page load timeout for {link}")
#                 continue  # Skip this entry

#             extracted_data = []

#             try:
#                 first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")
#                 first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
#                 print(f"Found {len(first_list_items)} items in the first list.")

#                 for item in first_list_items:
#                     driver.execute_script("arguments[0].click();", item)
#                     time.sleep(1)
#                     config_item = item.text.strip()
#                     print("Clicked an item in the first list.")

#                     previous_data = set()
#                     while True:
#                         try:
#                             nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
#                             nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
#                             print(f"Found {len(nested_list_items)} items in the nested list.")

#                             current_data = set()
#                             for sub_item in nested_list_items:
#                                 list_item_text = sub_item.text.strip()
#                                 current_data.add(list_item_text)
#                                 driver.execute_script("arguments[0].click();", sub_item)
#                                 time.sleep(1)
#                                 print(f"Clicked an item in the nested list: {list_item_text}")

#                                 # Extract price
#                                 # Extract price from the given XPath
#                                 try:
#                                     price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
#                                     price_text = price_element.text.strip()

#                                     # Switch to 2D and capture
#                                     try:
#                                         image_button_2d = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[2]/div/span[2]')
#                                         driver.execute_script("arguments[0].click();", image_button_2d)
#                                         #scroll to the image element
#                                         # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                                         time.sleep(1)

#                                         image_element_2d = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[2]/div/div/img')
#                                         download_and_rename_pdf(driver, xid, "2D_Floor_Plan", output_image_dir)
#                                         image_path_2d = os.path.join(output_image_dir, f"2d_floor_plan_{xid}_{config_item}_{list_item_text}.png")
#                                         image_element_2d.screenshot(image_path_2d)
                                    
#                                         print(f"2D floor plan image saved at {image_path_2d}")
#                                     except Exception as e:
#                                         print("Could not capture 2D image:")

#                                 except:
#                                     price_text = "Price not found"


#                                 # Write to CSV
#                                 with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#                                     writer = csv.writer(outcsv)
#                                     writer.writerow([xid, config_item ,list_item_text, price_text])
#                                     outcsv.flush()

#                             if current_data == previous_data:
#                                 print("No new data found. Ending pagination.")
#                                 break
#                             previous_data = current_data

#                         except StaleElementReferenceException:
#                             print("Stale element encountered. Retrying...")
#                             continue
#                         except:
#                             print("No nested list found under this item.")
#                             break

#                         try:
#                             next_button = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
#                             next_button_class = next_button.get_attribute("class")
#                             if "css-hskvoc" in next_button_class:
#                                 print("Next button is disabled. Ending pagination.")
#                                 break
#                             driver.execute_script("arguments[0].click();", next_button)
#                             time.sleep(2)
#                             print("Clicked 'Next' button.")
#                         except:
#                             print("No 'Next' button found or page did not change. Ending pagination.")
#                             break

#             except Exception as e:
#                 print(f"Error finding lists: {e}")

# print(f"Data extraction complete. Output saved to {output_file}")
# driver.quit()


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
from webdriver_manager.chrome import ChromeDriverManager
# Create folder if it doesn't exist
output_dir = os.path.join(os.getcwd(), "floor plans")
os.makedirs(output_dir, exist_ok=True)

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|\n\r]+', '_', name)  # Replace illegal characters
    return name.strip()


# Set up Selenium WebDriver
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# File names
input_file = 'input.csv'
output_file = 'output.csv'

# Read input CSV
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    # Open output CSV in append mode ('a') and write header if needed
    with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv)
        if outcsv.tell() == 0:  # Check if the file is empty
            writer.writerow(['XID', 'Configuration', 'List Item', 'Price', 'Area'])  # Write headers only if file is empty

    for row in reader:
        xid = row.get('XID', '').strip()
        link = row.get('Housing.com Link', '').strip()

        print("Processing XID:", xid, "Link:", link)

        if link.startswith('https://housing.com'):
            driver.get(link)
            time.sleep(2)  # Wait for the page to settle

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
                                    price_text = price_element.text.strip()
                                except:
                                    price_text = "Price not found"

                                

                                # Click 2D button and download image
                                try:
                                    # Click the 2D button
                                    two_d_button_xpath = '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[2]/div/span[2]'
                                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, two_d_button_xpath))).click()
                                    print("Clicked 2D floor plan button.")

                                    # Wait for image to appear
                                    img_xpath = '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/img'
                                    img_elem = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located((By.XPATH, img_xpath))
                                    )
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
                                            current_data["Area"] = carpet_area_text
                                        else:
                                            print("Carpet area info not found.")
                                            current_data["Area"] = "N/A"
                                    except Exception as e:
                                        print(f"Could not extract carpet area: {e}")
                                        current_data["carpet_area"] = "N/A"


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
                print(f"Error finding lists: {e}")

print(f"Data extraction complete. Output saved to {output_file}")
driver.quit()
