# import csv
# import time
# import os
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager

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
# input_csv = "urlsCrawled.csv"  # CSV file with links in a column named 'links'
# output_csv = "test.csv"

# with open(input_csv, mode='r', encoding='utf-8') as file:
#     reader = csv.DictReader(file)
#     links = [row['NoBroker.in Link'] for row in reader if row['NoBroker.in Link'].startswith("https://www.nobroker.in/")]

# # Check if output file exists and is empty
# file_exists = os.path.isfile(output_csv)
# write_header = not file_exists or os.stat(output_csv).st_size == 0

# # Open output CSV file in append mode
# with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     header = ["Name", "Rera ID", "NoBroker RERA ID", "Builder Project RERA ID", "Address", "Price Starting From", "Unit Configuration", "Parking", "Property Type", "Water Supply", "Builder", "Date of establishment", "Date of completion", "Units", "Min Flat Size", "Max Flat Size", "Project Area", "Min. Price", "Possesion Date", "Security", "Amenities", "Top Benefits"]
#     if write_header:
#         writer.writerow(header)

#     for link in links:
#         driver.get(link)
#         time.sleep(5)  # Wait for the page to load
#         print("Processing:", link)

#         # Extract details
#         def get_text(xpath):
#             try:
#                 return driver.find_element(By.XPATH, xpath).text.strip()
#             except:
#                 return "Not Found"

#         name = get_text('//*[@id="builderDetails"]/div[1]/div/div[1]/h1')
#         if name == "Not Found":
#             continue  # Skip writing if name is not found

#         address = get_text('//*[@id="builderDetails"]/div[1]/div/div[1]/div[1]/div')
#         price_starting = get_text('//*[@id="builderDetails"]/div[1]/div/div[2]/div[1]')

#         # Extract Top Benefits
#         try:
#             benefits_parent_div = driver.find_element(By.XPATH, '//h2[contains(text(), "Top Benefits")]/parent::div')
#             benefits_spans = benefits_parent_div.find_elements(By.XPATH, './/div/span')
#             top_benefits = ", ".join([span.text.strip() for span in benefits_spans if span.text.strip()])
#         except:
#             top_benefits = "Not Found"

#         # Click Overview tab
#         try:
#             overviewBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[1]')
#             driver.execute_script("arguments[0].click();", overviewBtn)
#             time.sleep(3)  # Wait for the tab to load
#         except:
#             pass

#         # Extract dynamic data
#         dynamic_fields = ["Unit Configuration", "Parking", "Property Type", "Water Supply", "Builder", "Date of establishment", "Date of completion", "Units", "Min Flat Size", "Max Flat Size", "Project Area", "Min. Price", "Possesion Date", "Security"]

#         def extract_sibling_text(label):
#             try:
#                 parent_div = driver.find_element(By.XPATH, f'//div[div[text()="{label}"]]')
#                 data_div = parent_div.find_element(By.XPATH, './div[1]')
#                 return data_div.text.strip()
#             except:
#                 return "Not Found"

#         dynamic_data = {field: extract_sibling_text(field) for field in dynamic_fields}

#         # Extract Amenities
#         try:
#             amenitiesBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[2]')
#             driver.execute_script("arguments[0].click();", amenitiesBtn)
#             time.sleep(3)  # Wait for the tab to load
#             amenities_elements = driver.find_elements(By.ID, "roomAmenities")
#             amenities = ", ".join([element.text.strip() for element in amenities_elements if element.text.strip()])
#         except:
#             amenities = "Not Found"

#         # Extract RERA IDs
#         def get_rera_id(label):
#             try:
#                 locationBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[5]')
#                 driver.execute_script("arguments[0].click();", locationBtn)
#                 driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.35);")
#                 time.sleep(3)
#                 parent_div = driver.find_element(By.XPATH, f'//div[div[text()="{label}"]]')
#                 data_div = parent_div.find_element(By.XPATH, './div[2]')
#                 return data_div.text.strip()
#             except:
#                 return "Not Found"

#         rera = get_rera_id("RERA ID")
#         nobrokerreraid = get_rera_id("NoBroker RERA ID")
#         builderprojectreraid = get_rera_id("Builder Project RERA ID")

#         # Write data immediately after processing each entry
#         writer.writerow([name, rera, nobrokerreraid, builderprojectreraid, address, price_starting] + [dynamic_data[field] for field in dynamic_fields] + [amenities, top_benefits])
#         file.flush()
#         os.fsync(file.fileno()) 

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
output_csv = "noBrokerFinalData2.csv"

with open(input_csv, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = [(row['XID'], row['NoBroker.in Link']) for row in reader if row['NoBroker.in Link'].startswith("https://www.nobroker.in/")]

# Check if output file exists and is empty
file_exists = os.path.isfile(output_csv)
write_header = not file_exists or os.stat(output_csv).st_size == 0

count = 0

# Open output CSV file in append mode
with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    header = ["xid", "Name", "Rera ID", "NoBroker RERA ID", "Builder Project RERA ID", "Address", "Price Starting From", "Unit Configuration", "Parking", "Property Type", "Water Supply", "Builder", "Date of establishment", "Date of completion", "Units", "Min Flat Size", "Max Flat Size", "Project Area", "Min. Price", "Possesion Date", "Security", "Amenities", "Top Benefits"]
    if write_header:
        writer.writerow(header)

    for xid, link in data:
        driver.get(link)
        time.sleep(5)  # Wait for the page to load
        print("Processing record :", count, link)

        # Extract details
        def get_text(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text.strip()
            except:
                return "Not Found"

        name = get_text('//*[@id="builderDetails"]/div[1]/div/div[1]/h1')
        if name == "Not Found":
            continue  # Skip writing if name is not found

        address = get_text('//*[@id="builderDetails"]/div[1]/div/div[1]/div[1]/div')
        price_starting = get_text('//*[@id="builderDetails"]/div[1]/div/div[2]/div[1]')

        # Extract Top Benefits
        try:
            benefits_parent_div = driver.find_element(By.XPATH, '//h2[contains(text(), "Top Benefits")]/parent::div')
            benefits_spans = benefits_parent_div.find_elements(By.XPATH, './/div/span')
            top_benefits = ", ".join([span.text.strip() for span in benefits_spans if span.text.strip()])
        except:
            top_benefits = "Not Found"

        # Extract dynamic data
        dynamic_fields = ["Unit Configuration", "Parking", "Property Type", "Water Supply", "Builder", "Date of establishment", "Date of completion", "Units", "Min Flat Size", "Max Flat Size", "Project Area", "Min. Price", "Possesion Date", "Security"]

        def extract_sibling_text(label):
            try:
                parent_div = driver.find_element(By.XPATH, f'//div[div[text()="{label}"]]')
                data_div = parent_div.find_element(By.XPATH, './div[1]')
                return data_div.text.strip()
            except:
                return "Not Found"

        dynamic_data = {field: extract_sibling_text(field) for field in dynamic_fields}

        # Extract Amenities
        try:
            amenitiesBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[2]')
            driver.execute_script("arguments[0].click();", amenitiesBtn)
            time.sleep(3)  # Wait for the tab to load
            amenities_elements = driver.find_elements(By.ID, "roomAmenities")
            amenities = ", ".join([element.text.strip() for element in amenities_elements if element.text.strip()])
        except:
            amenities = "Not Found"

        # Extract RERA IDs
        def get_rera_id(label):
            try:
                locationBtn = driver.find_element(By.XPATH, '//*[@id="categoryHeaderWrapper"]/span[5]')
                driver.execute_script("arguments[0].click();", locationBtn)
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight * 0.35);")
                time.sleep(3)
                parent_div = driver.find_element(By.XPATH, f'//div[div[text()="{label}"]]')
                data_div = parent_div.find_element(By.XPATH, './div[2]')
                return data_div.text.strip()
            except:
                return "Not Found"

        rera = get_rera_id("RERA ID")
        nobrokerreraid = get_rera_id("NoBroker RERA ID")
        builderprojectreraid = get_rera_id("Builder Project RERA ID")

        # Write data immediately after processing each entry
        writer.writerow([xid, name, rera, nobrokerreraid, builderprojectreraid, address, price_starting] + [dynamic_data[field] for field in dynamic_fields] + [amenities, top_benefits])
        file.flush()
        os.fsync(file.fileno()) 

        count += 1

# Quit WebDriver
driver.quit()
print("Data extraction completed.")