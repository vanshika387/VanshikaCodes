# import os
# import csv
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # Setup Chrome Options
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# options.add_argument('start-maximized')
# options.add_argument("--log-level=3")

# # Initialize WebDriver
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
# wait = WebDriverWait(driver, 10)

# # Read CSV file containing property links
# input_csv = "noBrokerUrls.csv"  # CSV file with links in a column named 'NoBroker.in Link' and 'xid'
# output_csv = "finalData.csv"

# with open(input_csv, mode='r', encoding='utf-8') as file:
#     reader = csv.DictReader(file)
#     data = [(row['XID'], row['NoBroker.in Link']) for row in reader if row['NoBroker.in Link'].startswith("https://www.nobroker.in/")]

# # Check if output file exists and is empty
# file_exists = os.path.isfile(output_csv)
# write_header = not file_exists or os.stat(output_csv).st_size == 0

# # Open output CSV file in append mode
# with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     header = ["xid", "Project Name", "Configuration", "Area", "Price"]
#     if write_header:
#         writer.writerow(header)

#     for xid, link in data:
#         driver.get(link)
#         time.sleep(5)  # Wait for the page to load
#         print("Processing:", xid, link)

#         # Extract project name
#         try:
#             project_name = driver.find_element(By.XPATH, '//*[@id="builderDetails"]/div[1]/div/div[1]/h1').text.strip()
#         except:
#             project_name = "Not Found"

#         if project_name == "Not Found":
#             continue  # Skip writing if project name is not found

#         # Click Floor Plan tab
#         try:
#             floorPlanBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[3]')
#             driver.execute_script("arguments[0].click();", floorPlanBtn)
#             time.sleep(3)  # Wait for the tab to load
#         except:
#             continue  # Skip if floor plan tab is not found

#         # Extract all floor plans
#         try:
#             floor_plan_divs = driver.find_elements(By.CLASS_NAME, "card-wrapper.mr-4")
#             for div in floor_plan_divs:
#                 try:
#                     configuration = div.find_element(By.CLASS_NAME, "heading-6").text.strip()
#                     area = div.find_element(By.CLASS_NAME, "heading-7").text.strip()
#                     price = div.find_element(By.ID, "requestPriceDetails").text.strip()
#                 except:
#                     configuration, area, price = "Not Found", "Not Found", "Not Found"
                
#                 # Write data to CSV
#                 writer.writerow([xid, project_name, configuration, area, price])
#                 file.flush()
#                 os.fsync(file.fileno()) 
#         except:
#             pass  # No floor plans found

# # Quit WebDriver
# driver.quit()
# print("Data extraction completed.")

import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup Chrome Options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('start-maximized')
options.add_argument("--log-level=3")

# Initialize WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Read CSV file containing property links
input_csv = "noBrokerUrls2.csv"  # CSV file with links in a column named 'NoBroker.in Link' and 'xid'
output_csv = "noBrokerFloorPlans2.csv"

with open(input_csv, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = [(row['XID'], row['NoBroker.in Link']) for row in reader if row['NoBroker.in Link'].startswith("https://www.nobroker.in/")]

# Check if output file exists and is empty
file_exists = os.path.isfile(output_csv)
write_header = not file_exists or os.stat(output_csv).st_size == 0

# Open output CSV file in append mode
with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    header = ["xid", "Project Name", "Configuration", "Area", "Price"]
    if write_header:
        writer.writerow(header)

    for xid, link in data:
        driver.get(link)
        time.sleep(5)  # Wait for the page to load
        print("Processing:", xid, link)

        # Extract project name
        try:
            project_name = driver.find_element(By.XPATH, '//*[@id="builderDetails"]/div[1]/div/div[1]/h1').text.strip()
        except:
            project_name = "Not Found"

        if project_name == "Not Found":
            continue  # Skip writing if project name is not found

        # Click Floor Plan tab
        try:
            floorPlanBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[3]')
            driver.execute_script("arguments[0].click();", floorPlanBtn)
            time.sleep(3)  # Wait for the tab to load
        except:
            continue  # Skip if floor plan tab is not found

        # Extract all floor plans
        try:
            floor_plan_divs = driver.find_elements(By.CLASS_NAME, "card-wrapper")
            for div in floor_plan_divs:
                try:
                    configuration = div.find_element(By.CLASS_NAME, "heading-6").text.strip()
                    area = div.find_element(By.CLASS_NAME, "heading-7").text.strip()
                    
                    # Extract price dynamically
                    try:
                        price = div.find_element(By.XPATH, ".//div[contains(@class, 'cursor-pointer')]/span").text.strip()
                    except:
                        price = "Not Found"
                except:
                    configuration, area, price = "Not Found", "Not Found", "Not Found"
                
                # Write data to CSV
                writer.writerow([xid, project_name, configuration, area, price])
                file.flush()
                os.fsync(file.fileno()) 
        except:
            pass  # No floor plans found

# Quit WebDriver
driver.quit()
print("Data extraction completed.")