# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Setup Selenium WebDriver
# driver = webdriver.Chrome()
# wait = WebDriverWait(driver, 10)

# # Load input CSV (skip header)
# input_file = "input.csv"
# with open(input_file, newline='', encoding='utf-8') as f:
#     reader = csv.reader(f)
#     next(reader)  # Skip header
#     data_rows = list(reader)

# # Output files
# floor_plan_csv_filename = "square_yards_floor_plans3.csv"
# main_output_csv = "test3.csv"

# # Prepare floor plan CSV
# with open(floor_plan_csv_filename, "w", newline="", encoding="utf-8") as fp_file:
#     fp_writer = csv.writer(fp_file)
#     fp_writer.writerow(["XID", "Project Name", "Unit Type", "Area", "Price"])

# # Iterate over each project
# for row in data_rows:
#     url, xid = row[4].strip(), row[0].strip()
#     driver.get(url)
#     time.sleep(3)

#     # Extract project name
#     try:
#         project_name = driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
#     except:
#         project_name = "N/A"

#     try:
#         price_list_tab = driver.find_element(By.XPATH, "//li[@data-tab='npPriceList']")
#         driver.execute_script("arguments[0].click();", price_list_tab)
#         time.sleep(3)
#     except:
#         print("Price List tab not found.")

#     try:
#         price_table = driver.find_element(By.CSS_SELECTOR, ".npTableBox.scrollBarHide.active")
#         rows = price_table.find_elements(By.CSS_SELECTOR, "tbody tr")
#     except:
#         print("No active price table found.")
#         rows = []


#     # Extract all floor plan details from this table
#     floor_plans = []
#     for row in rows:
#         try:
#             unit_type = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) strong").text.strip()
#             area = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) span").text.strip()
#             price = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span").text.strip()
#             price = price.replace("₹", "Rs").strip()
#             floor_plans.append((unit_type, area, price))
#         except:
#             continue


#     floor_plan_csv_filename = "square_yards_floor_plans4.csv"
#     with open(floor_plan_csv_filename, "a", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)
#         if(file.tell() == 0):
#             writer.writerow(["XID","Project Name", "Unit Type", "Area", "Price"])
#         for plan in floor_plans:
#             writer.writerow([xid,project_name, *plan])

#     print(f"Floor plan data saved to {floor_plan_csv_filename}")


# # Close browser
# driver.quit()

import csv
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Selenium WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Define output folder for images
output_folder = "output_images"
os.makedirs(output_folder, exist_ok=True)

# Load input CSV (skip header)
input_file = "input.csv"
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    data_rows = list(reader)

# Output files
floor_plan_csv_filename = "square_yards_floor_plansjhhhhh.csv"
main_output_csv = "testhhhhh.csv"

# Prepare floor plan CSV
with open(floor_plan_csv_filename, "w", newline="", encoding="utf-8") as fp_file:
    fp_writer = csv.writer(fp_file)
    fp_writer.writerow(["XID", "Project Name", "Unit Type", "Area", "Price"])

# Iterate over each project
for row in data_rows:
    url, xid = row[4].strip(), row[0].strip()
    driver.get(url)
    time.sleep(3)

    # Extract project name
    try:
        project_name = driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
    except:
        project_name = "N/A"

    try:
        price_list_tab = driver.find_element(By.XPATH, "//li[@data-tab='npPriceList']")
        driver.execute_script("arguments[0].click();", price_list_tab)
        time.sleep(3)
    except:
        print("Price List tab not found.")

    try:
        price_table = driver.find_element(By.CSS_SELECTOR, ".npTableBox.scrollBarHide.active")
        rows = price_table.find_elements(By.CSS_SELECTOR, "tbody tr")
    except:
        print("No active price table found.")
        rows = []

    # Extract all floor plan details from this table
    floor_plans = []
    for row in rows:
        try:
            unit_type = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) strong").text.strip()
            area = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) span").text.strip()
            price = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span").text.strip()
            price = price.replace("₹", "Rs").strip()
            floor_plans.append((unit_type, area, price))
        except:
            continue

    floor_plan_csv_filename = "square_yards_floor_plans4.csv"
    with open(floor_plan_csv_filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if(file.tell() == 0):
            writer.writerow(["XID","Project Name", "Unit Type", "Area", "Price"])
        for plan in floor_plans:
            writer.writerow([xid,project_name, *plan])

    print(f"Floor plan data saved to {floor_plan_csv_filename}")

    try:
        # Click the Floor Plans tab
        floor_tab = driver.find_element(By.XPATH, '//*[@id="#floorPlans"]')
        driver.execute_script("arguments[0].click();", floor_tab)
        print("Clicked on Floor Plans tab.")
        time.sleep(3)

        # Find all floor plan tab containers
        floor_plan_tabs = driver.find_elements(By.CSS_SELECTOR, ".npTab.scrollBarHide.floorPlanLi")

        for container_index, container in enumerate(floor_plan_tabs, 1):
            list_items = container.find_elements(By.TAG_NAME, "li")

            for idx, li in enumerate(list_items):
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", li)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", li)
                    print(f"Clicked floor plan item #{idx} in container #{container_index}")
                    time.sleep(2)

                    # Find all floor plan images
                    images = driver.find_elements(By.CSS_SELECTOR, "img.img-responsive.lazy.loadGallery.floorPlans")

                    for imgcnt, img in enumerate(images):
                        try:
                            twodButton = driver.find_element(By.CLASS_NAME, 'switchItem.dev_2dbtn')
                            if twodButton:
                                driver.execute_script("arguments[0].click();", twodButton)
                                print("Clicked 2D button.")
                                time.sleep(1)
                            else:
                                print("2D button is not interactable.")
                        except Exception as e:
                            print(f"2D button not found or error occurred")

                        img_src = img.get_attribute("src")
                        img_alt = img.get_attribute("alt").replace(" ", "_").replace("/", "_")

                        if img_src and img_alt:
                            filename = f"{xid}_{img_alt}.jpg"
                            filepath = os.path.join(output_folder, filename)

                            try:
                                response = requests.get(img_src, stream=True)
                                if response.status_code == 200:
                                    with open(filepath, "wb") as f:
                                        for chunk in response.iter_content(1024):
                                            f.write(chunk)
                                    print(f"Downloaded image: {filename}")
                                else:
                                    print(f"Failed to download image from {img_src}")
                            except Exception as e:
                                print(f"Error downloading image {filename}")

                        # Click the "next" button after every 2 images
                        if (imgcnt + 1) % 2 == 0:
                            try:
                                # Restrict the search for the next button to the visible viewport
                                next_button = driver.find_element(By.CSS_SELECTOR, '.bx-next:visible')
                                if next_button:
                                    driver.execute_script("arguments[0].click();", next_button)
                                    print("Clicked next button.")
                                    time.sleep(2)
                            except Exception as e:
                                print("Next button is not clickable or not found in the viewport.")
                except Exception as e:
                    print(f"Error clicking floor plan item #{idx} in container #{container_index}")
    except Exception as e:
        print(f"Error accessing floor plans: {e}")

# Close browser
driver.quit()
.....................

import csv
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Selenium WebDriver
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Define output folder for images
output_folder = "floor plans"
os.makedirs(output_folder, exist_ok=True)

# Load input CSV (skip header)
input_file = "outputUrls1.csv"
with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    data_rows = list(reader)

# Output files
floor_plan_csv_filename = "SquareyardsOptionsData1.csv"
main_output_csv = "test.csv"

# Prepare floor plan CSV
with open(floor_plan_csv_filename, "a", newline="", encoding="utf-8") as fp_file:
    fp_writer = csv.writer(fp_file)
    if fp_file.tell() == 0:  # Check if file is empty to write header
        fp_writer.writerow(["XID", "Project Name", "Unit Type", "Area", "Price"])

# Iterate over each project
for row in data_rows:
    url, xid = row[3].strip(), row[0].strip()
    if url.endswith("/project"):
        driver.get(url)
        time.sleep(3)
    else:
        continue

    # Extract project name
    try:
        project_name = driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
    except:
        project_name = "N/A"

    try:
        price_list_tab = driver.find_element(By.XPATH, "//li[@data-tab='npPriceList']")
        driver.execute_script("arguments[0].click();", price_list_tab)
        time.sleep(3)
    except:
        print("Price List tab not found.")

    try:
        price_table = driver.find_element(By.CSS_SELECTOR, ".npTableBox.scrollBarHide.active")
        rows = price_table.find_elements(By.CSS_SELECTOR, "tbody tr")
    except:
        print("No active price table found.")
        rows = []

    # Extract all floor plan details from this table
    floor_plans = []
    for row in rows:
        try:
            unit_type = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) strong").text.strip()
            area = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) span").text.strip()
            price = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span").text.strip()
            price = price.replace("₹", "Rs").strip()
            floor_plans.append((unit_type, area, price))
        except:
            continue

    # Write to CSV
    with open(floor_plan_csv_filename, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for plan in floor_plans:
            writer.writerow([xid, project_name, *plan])

    print(f"Floor plan data saved to {floor_plan_csv_filename}")

    # Process floor plan images
    try:
        # Click the Floor Plans tab
        floor_tab = driver.find_element(By.XPATH, '//*[@id="#floorPlans"]')
        driver.execute_script("arguments[0].click();", floor_tab)
        print("Clicked on Floor Plans tab.")
        time.sleep(3)

        # Find all floor plan tab containers
        floor_plan_tabs = driver.find_elements(By.CSS_SELECTOR, ".npTab.scrollBarHide.floorPlanLi")

        for container_index, container in enumerate(floor_plan_tabs, 1):
            list_items = container.find_elements(By.TAG_NAME, "li")
            print(f"Found {len(list_items)} floor plan types in container #{container_index}")

            for idx, li in enumerate(list_items):
                print(f"Processing floor plan type #{idx+1} of {len(list_items)}")
                try:
                    # Ensure the element is in view before clicking
                    driver.execute_script("arguments[0].scrollIntoView(true);", li)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", li)
                    print(f"Clicked floor plan item #{idx+1} in container #{container_index}")
                    time.sleep(2)
                    
                    # Keep track of images we've seen to avoid getting stuck
                    seen_images = set()
                    no_new_images_count = 0
                    max_no_new_attempts = 3  # If we go 3 rounds without new images, assume we're done
                    
                    # Process all visible cards first
                    visible_cards = driver.find_elements(By.CSS_SELECTOR, ".unitCard:not([aria-hidden='true'])")
                    print(f"Found {len(visible_cards)} initially visible cards")
                    
                    for card in visible_cards:
                        try:
                            # Scroll to the card
                            driver.execute_script("arguments[0].scrollIntoView(true);", card)
                            time.sleep(0.5)
                            
                            # Try to click 2D button if it exists
                            try:
                                twodButton = card.find_element(By.CLASS_NAME, 'switchItem.dev_2dbtn')
                                if twodButton.is_displayed():
                                    driver.execute_script("arguments[0].click();", twodButton)
                                    print("Clicked 2D button.")
                                    time.sleep(1)
                            except:
                                pass  # 2D button might not exist
                            
                            # Find and download the image
                            try:
                                img = card.find_element(By.CSS_SELECTOR, "img.img-responsive.loadGallery.floorPlans")
                                img_src = img.get_attribute("src")
                                img_alt = img.get_attribute("alt").replace(" ", "_").replace("/", "_")
                                
                                if img_src and img_alt:
                                    # Add to our set of seen images
                                    image_id = f"{img_src}_{img_alt}"
                                    seen_images.add(image_id)
                                    
                                    filename = f"{xid}_{img_alt}.jpg"
                                    filepath = os.path.join(output_folder, filename)
                                    
                                    if not os.path.exists(filepath):
                                        try:
                                            response = requests.get(img_src, stream=True)
                                            if response.status_code == 200:
                                                with open(filepath, "wb") as f:
                                                    for chunk in response.iter_content(1024):
                                                        f.write(chunk)
                                                print(f"Downloaded image: {filename}")
                                            else:
                                                print(f"Failed to download image from {img_src}")
                                        except Exception as e:
                                            print(f"Error downloading image {filename}: {str(e)}")
                            except:
                                print("No image found in this card")
                        except Exception as e:
                            print(f"Error processing card: {str(e)}")
                    
                    # Navigate through slides
                    max_slides = 10  # Safety limit
                    slide_count = 0
                    
                    while slide_count < max_slides and no_new_images_count < max_no_new_attempts:
                        # Try to find and click the next button
                        try:
                            # Find all next buttons and click the one that's visible
                            next_buttons = driver.find_elements(By.CSS_SELECTOR, ".bx-next")
                            next_button = None
                            
                            for btn in next_buttons:
                                if btn.is_displayed():
                                    next_button = btn
                                    break
                            
                            if next_button:
                                # Click the next button
                                driver.execute_script("arguments[0].click();", next_button)
                                print(f"Clicked next button (slide {slide_count + 1})")
                                time.sleep(2)  # Wait for new slides
                                slide_count += 1
                                
                                # Find newly visible cards
                                current_image_count = len(seen_images)
                                new_cards = driver.find_elements(By.CSS_SELECTOR, ".unitCard:not([aria-hidden='true'])")
                                print(f"Found {len(new_cards)} cards after clicking next")
                                
                                # Process new cards
                                for card in new_cards:
                                    try:
                                        # Scroll to the card
                                        driver.execute_script("arguments[0].scrollIntoView(true);", card)
                                        time.sleep(0.5)
                                        
                                        # Try 2D button if it exists
                                        try:
                                            twodButton = card.find_element(By.CLASS_NAME, 'switchItem.dev_2dbtn')
                                            if twodButton.is_displayed():
                                                driver.execute_script("arguments[0].click();", twodButton)
                                                print("Clicked 2D button on new slide.")
                                                time.sleep(1)
                                        except:
                                            pass
                                        
                                        # Get the image
                                        try:
                                            img = card.find_element(By.CSS_SELECTOR, "img.img-responsive.loadGallery.floorPlans")
                                            img_src = img.get_attribute("src")
                                            img_alt = img.get_attribute("alt").replace(" ", "_").replace("/", "_")
                                            
                                            if img_src and img_alt:
                                                # Check if we've seen this image before
                                                image_id = f"{img_src}_{img_alt}"
                                                
                                                if image_id not in seen_images:
                                                    seen_images.add(image_id)
                                                    
                                                    filename = f"{xid}_{img_alt}.jpg"
                                                    filepath = os.path.join(output_folder, filename)
                                                    
                                                    if not os.path.exists(filepath):
                                                        try:
                                                            response = requests.get(img_src, stream=True)
                                                            if response.status_code == 200:
                                                                with open(filepath, "wb") as f:
                                                                    for chunk in response.iter_content(1024):
                                                                        f.write(chunk)
                                                                print(f"Downloaded image: {filename}")
                                                            else:
                                                                print(f"Failed to download image from {img_src}")
                                                        except Exception as e:
                                                            print(f"Error downloading image {filename}: {str(e)}")
                                        except:
                                            print("No image found in this new card")
                                    except Exception as e:
                                        print(f"Error processing new card: {str(e)}")
                                
                                # Check if we found any new images
                                if len(seen_images) > current_image_count:
                                    # Reset counter if we found new images
                                    no_new_images_count = 0
                                else:
                                    # Increment counter if we didn't find new images
                                    no_new_images_count += 1
                                    print(f"No new images found in this slide. Counter: {no_new_images_count}/{max_no_new_attempts}")
                            else:
                                print("No more visible next buttons found, moving to next floor plan")
                                break
                        except Exception as e:
                            print(f"Error navigating slides: {str(e)}")
                            break
                    
                    print(f"Done processing floor plan type #{idx+1}. Moving to next type.")
                    
                except Exception as e:
                    print(f"Error processing floor plan type #{idx+1}: {str(e)}")
    except Exception as e:
        print(f"Error accessing floor plans: {str(e)}")

# Close browser
driver.quit()