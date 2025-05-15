# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Selenium WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # File names
# input_file = 'housingLinks.csv'
# output_file = 'output.csv'

# # Read input CSV
# with open(input_file, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     # Open output CSV in append mode ('a') and write header if needed
#     with open(output_file, 'w', newline='', encoding='utf-8') as outcsv:
#         writer = csv.writer(outcsv)
#         writer.writerow(['XID', 'Extracted Data'])  # Write the header only once

#     for row in reader:
#         xid = row.get('XID', '').strip()
#         link = row.get('Housing.com Link', '').strip()

#         print("Processing XID:", xid, "Link:", link)

#         if link != 'Not Found':
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
#                 extracted_data = "Page load timeout"
#                 continue  # Skip this entry

#             # Find the list with class "config-header-container css-n0tp0a"
#             try:
#                 list_container = WebDriverWait(driver, 5).until(
#                     EC.presence_of_element_located((By.CLASS_NAME, 'config-header-container.css-n0tp0a'))
#                 )
#                 list_items = list_container.find_elements(By.TAG_NAME, "li")  # Get all list items
#                 print(f"Found {len(list_items)} list items.")

#                 for item in list_items:
#                     driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
#                     time.sleep(1)  # Give it some time after each click
#                     print("Clicked a list item.")
                
#                 extracted_data = "Clicked all list items"  # Placeholder

#             except:
#                 print("List container or items not found.")
#                 extracted_data = "List not found"

#             # Append data to CSV immediately
#             with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#                 writer = csv.writer(outcsv)
#                 writer.writerow([xid, extracted_data])
#                 outcsv.flush()  # Ensure data is written to file immediately

# print(f"Data extraction complete. Output saved to {output_file}")
# driver.quit()

# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Selenium WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # File names
# input_file = 'housingLinks.csv'
# output_file = 'output.csv'

# # Read input CSV
# with open(input_file, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     # Open output CSV in append mode ('a') and write header if needed
#     with open(output_file, 'w', newline='', encoding='utf-8') as outcsv:
#         writer = csv.writer(outcsv)
#         writer.writerow(['XID', 'Extracted Data'])  # Write the header only once

#     for row in reader:
#         xid = row.get('XID', '').strip()
#         link = row.get('Housing.com Link', '').strip()

#         print("Processing XID:", xid, "Link:", link)

#         if link != 'Not Found':
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
#                 extracted_data = "Page load timeout"
#                 continue  # Skip this entry

#             extracted_data = []  # Store extracted data

#             # Find all containers with class "config-header-container css-n0tp0a"
#             try:
#                 first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")  # The first one is the main list
#                 first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
#                 print(f"Found {len(first_list_items)} items in the first list.")

#                 for item in first_list_items:
#                     driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
#                     time.sleep(1)
#                     print("Clicked an item in the first list.")

#                     # Look for a nested list inside THIS item (not globally)
#                     try:
#                         nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
#                         nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
#                         print(f"Found {len(nested_list_items)} items in the nested list.")

#                         for sub_item in nested_list_items:
#                             driver.execute_script("arguments[0].click();", sub_item)  # Click via JavaScript
#                             time.sleep(1)
#                             print("Clicked an item in the nested list.")

#                         extracted_data.append("Clicked all nested items")
#                     except:
#                         print("No nested list found under this item.")
#                         extracted_data.append("No nested list found")

#             except Exception as e:
#                 print(f"Error finding lists: {e}")
#                 extracted_data.append("Lists not found")

#             # Append data to CSV immediately
#             with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#                 writer = csv.writer(outcsv)
#                 writer.writerow([xid, " | ".join(extracted_data)])
#                 outcsv.flush()  # Ensure data is written to file immediately

# print(f"Data extraction complete. Output saved to {output_file}")
# driver.quit()

# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Selenium WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # File names
# input_file = 'housingLinks.csv'
# output_file = 'output.csv'

# # Read input CSV
# with open(input_file, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     # Open output CSV in append mode ('a') and write header if needed
#     with open(output_file, 'w', newline='', encoding='utf-8') as outcsv:
#         writer = csv.writer(outcsv)
#         writer.writerow(['XID', 'List Item', 'Price'])  # Updated headers

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

#             extracted_data = []  # Store extracted data

#             # Find all containers with class "config-header-container css-n0tp0a"
#             try:
#                 first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")  # The first one is the main list
#                 first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
#                 print(f"Found {len(first_list_items)} items in the first list.")

#                 for item in first_list_items:
#                     driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
#                     time.sleep(1)
#                     print("Clicked an item in the first list.")

#                     # Look for a nested list inside THIS item (not globally)
#                     try:
#                         nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
#                         nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
#                         print(f"Found {len(nested_list_items)} items in the nested list.")

#                         for sub_item in nested_list_items:
#                             list_item_text = sub_item.text.strip()  # Get the text of the sub-item
#                             driver.execute_script("arguments[0].click();", sub_item)  # Click via JavaScript
#                             time.sleep(1)
#                             print(f"Clicked an item in the nested list: {list_item_text}")

#                             # Extract price from the given XPath
#                             try:
#                                 price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
#                                 price_text = price_element.text.strip()
#                             except:
#                                 price_text = "Price not found"

#                             # Append row immediately to CSV
#                             with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#                                 writer = csv.writer(outcsv)
#                                 writer.writerow([xid, list_item_text, price_text])
#                                 outcsv.flush()  # Ensure data is written immediately

#                     except:
#                         print("No nested list found under this item.")

#             except Exception as e:
#                 print(f"Error finding lists: {e}")

# print(f"Data extraction complete. Output saved to {output_file}")
# driver.quit()
# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # Set up Selenium WebDriver
# options = Options()
# options.add_argument('--disable-gpu')
# options.add_argument('--no-sandbox')
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# # File names
# input_file = 'housingLinks.csv'
# output_file = 'output.csv'

# # Read input CSV
# with open(input_file, newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile)
    
#     # Open output CSV in append mode ('a') and write header if needed
#     with open(output_file, 'w', newline='', encoding='utf-8') as outcsv:
#         writer = csv.writer(outcsv)
#         writer.writerow(['XID', 'List Item', 'Price'])  # Updated headers

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

#             extracted_data = []  # Store extracted data

#             # Find all containers with class "config-header-container css-n0tp0a"
#             try:
#                 first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")  # The first one is the main list
#                 first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
#                 print(f"Found {len(first_list_items)} items in the first list.")

#                 for item in first_list_items:
#                     driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
#                     time.sleep(1)
#                     print("Clicked an item in the first list.")

#                     while True:
#                         # Look for a nested list inside THIS item (not globally)
#                         try:
#                             nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
#                             nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
#                             print(f"Found {len(nested_list_items)} items in the nested list.")

#                             for sub_item in nested_list_items:
#                                 list_item_text = sub_item.text.strip()  # Get the text of the sub-item
#                                 driver.execute_script("arguments[0].click();", sub_item)  # Click via JavaScript
#                                 time.sleep(1)
#                                 print(f"Clicked an item in the nested list: {list_item_text}")

#                                 # Extract price from the given XPath
#                                 try:
#                                     price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
#                                     price_text = price_element.text.strip()
#                                 except:
#                                     price_text = "Price not found"

#                                 # Append row immediately to CSV
#                                 with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
#                                     writer = csv.writer(outcsv)
#                                     writer.writerow([xid, list_item_text, price_text])
#                                     outcsv.flush()  # Ensure data is written immediately
                        
#                         except:
#                             print("No nested list found under this item.")
#                             break
                        
#                         # Check for the Next button
#                         try:
#                             next_button = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
#                             if "disabled" not in next_button.get_attribute("class"):
#                                 driver.execute_script("arguments[0].click();", next_button)
#                                 time.sleep(2)
#                                 print("Clicked 'Next' button.")
#                             else:
#                                 print("Next button is disabled. Ending pagination.")
#                                 break
#                         except:
#                             print("No 'Next' button found. Ending pagination.")
#                             break
            
#             except Exception as e:
#                 print(f"Error finding lists: {e}")

# print(f"Data extraction complete. Output saved to {output_file}")
# driver.quit()

import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# File names
input_file = 'noida697.csv'
output_file = 'noida697FloorPlanData.csv'

# Read input CSV
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # Open output CSV in append mode ('a') and write header if needed
    with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv)
        if outcsv.tell() == 0:  # Check if the file is empty
            writer.writerow(['XID', 'Configuration', 'List Item', 'Price'])  # Write headers only if file is empty

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

            extracted_data = []  # Store extracted data

            # Find all containers with class "config-header-container css-n0tp0a"
            try:
                first_list_container = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")  # The first one is the main list
                first_list_items = first_list_container.find_elements(By.TAG_NAME, "li")
                print(f"Found {len(first_list_items)} items in the first list.")

                for item in first_list_items:
                    driver.execute_script("arguments[0].click();", item)  # Click via JavaScript
                    time.sleep(1)
                    config_item = item.text.strip()  # Get the text of the clicked item
                    print("Clicked an item in the first list.")

                    previous_data = set()
                    while True:
                        # Look for a nested list inside THIS item (not globally)
                        try:
                            nested_list_container = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
                            nested_list_items = nested_list_container.find_elements(By.TAG_NAME, "li")
                            print(f"Found {len(nested_list_items)} items in the nested list.")

                            current_data = set()
                            for sub_item in nested_list_items:
                                list_item_text = sub_item.text.strip()  # Get the text of the sub-item
                                current_data.add(list_item_text)
                                driver.execute_script("arguments[0].click();", sub_item)  # Click via JavaScript
                                time.sleep(1)
                                print(f"Clicked an item in the nested list: {list_item_text}")

                                # Extract price from the given XPath
                                try:
                                    price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
                                    price_text = price_element.text.strip()
                                except:
                                    price_text = "Price not found"

                                # Append row immediately to CSV
                                with open(output_file, 'a', newline='', encoding='utf-8') as outcsv:
                                    writer = csv.writer(outcsv)
                                    writer.writerow([xid, config_item ,list_item_text, price_text])
                                    outcsv.flush()  # Ensure data is written immediately

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
                        
                        # Check for the Next button
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
