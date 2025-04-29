# import csv
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service as ChromeService
# import time
# import os
# import re

# # Read registration numbers from focus.csv (without using pandas)
# registration_numbers = []
# with open('bihar/focus.csv', 'r', encoding='utf-8') as file:
#     reader = csv.DictReader(file)
#     for row in reader:
#         reg = row.get('Reg.')
#         if reg:
#             registration_numbers.append(reg.strip())

# # Setup Chrome Options
# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--ignore-ssl-errors')
# # options.add_argument('--headless')  # Optional
# options.add_argument('start-maximized')
# options.add_argument("--log-level=3")

# # Initialize WebDriver
# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
# wait = WebDriverWait(driver, 10)

# # Open Bihar RERA page
# driver.get('https://rera.bihar.gov.in/RegisteredPP.aspx')

# # Create directory for QR codes if not exists
# # if not os.path.exists("QR_Codes"):
# #     os.makedirs("QR_Codes")

# for regnum in registration_numbers:
#     try:
#         # Sanitize filename
#         clean_regnum = re.sub(r'[\/:*?"<>|]', '_', regnum)
#         if not clean_regnum:
#             continue

#         print(f"Processing: {clean_regnum}")

#         # Enter regnum into the search field
#         time.sleep(5)  # Wait for the page to load
#         search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_txtSearch"]')))
#         search_input.clear()
#         search_input.send_keys(regnum)

#         # Press Enter
#         search_input.submit()

#         time.sleep(5)  # Give some time for results to load

#         try: 

#             # Click the first result link
#             project_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_GV_Building"]/tbody/tr[2]/td[1]/a')))
#             # ActionChains(driver).move_to_element(project_link).click().perform()
#             driver.execute_script("arguments[0].click();", project_link)

#             time.sleep(5)
#         except:
#             print(f"Project link not found for {regnum}")
#             continue

#         # Switch to new tab
#         wait.until(EC.number_of_windows_to_be(2))
#         new_window = [handle for handle in driver.window_handles if handle != driver.current_window_handle][0]
#         driver.switch_to.window(new_window)

#         time.sleep(15)  # Wait for the new tab to load

#         # Wait until the new window is fully loaded
#         wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

#         time.sleep(3)
#         try:
#             # Extract table data
#             table = driver.find_element(By.XPATH, '//*[@id="GV_Building"]')
#             # driver.execute_script("arguments[0].scrollIntoView();", table)  # Scroll to the table
#             time.sleep(1)  # Wait for the table to be in view
#             rows = table.find_elements(By.TAG_NAME, 'tr')

#             # Open CSV file in append mode
#             with open('bihar/output.csv', 'a', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.writer(csvfile)

#                 # Write headers only once
#                 if csvfile.tell() == 0:  # Check if file is empty
#                     headers = ['Reg. No'] + [header.text for header in rows[0].find_elements(By.TAG_NAME, 'th')]
#                     writer.writerow(headers)

#                 # Write table rows
#                 for row in rows[1:]:  # Skip header row
#                     cells = [regnum] + [cell.text for cell in row.find_elements(By.TAG_NAME, 'td')]
#                     writer.writerow(cells)

#                 print(f"Data saved for {regnum}")
#         except:
            
#             print(f"Table not found for {regnum}")

#         # Close the tab and switch back
#         if(len(driver.window_handles) > 1):
#             driver.close()
#             driver.switch_to.window(driver.window_handles[0])
#         # driver.close()
#         driver.switch_to.window(driver.window_handles[0])

#     except Exception as e:
#         print(f"Error processing {regnum}: {e}")
#         driver.refresh()
#         time.sleep(2)

# # Quit browser
# driver.quit()

import csv
import time
import os
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

# --- Setup ---

# Read registration numbers from CSV
registration_numbers = []
with open('bihar/focus.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        reg = row.get('Reg.')
        if reg:
            registration_numbers.append(reg.strip())

# Setup Chrome
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('start-maximized')
options.add_argument("--log-level=3")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 15)

# Create output directory if needed
output_path = 'bihar/output.csv'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Open Bihar RERA main page
driver.get('https://rera.bihar.gov.in/RegisteredPP.aspx')

# --- Main Processing ---

for regnum in registration_numbers:
    try:
        # Clean regnum for filename safety (not for search)
        clean_regnum = re.sub(r'[\/:*?"<>|]', '_', regnum)
        if not clean_regnum:
            continue

        print(f"\nProcessing: {clean_regnum}")

        # Always go fresh to search page (to avoid session expiration)
        driver.get('https://rera.bihar.gov.in/RegisteredPP.aspx')

        # Wait for search field to appear
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_txtSearch"]')))
        search_input.clear()
        search_input.send_keys(regnum)
        search_input.submit()

        # Wait for results
        try:
            project_link = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_GV_Building"]/tbody/tr[2]/td[1]/a')))
            driver.execute_script("arguments[0].click();", project_link)
        except:
            print(f"❌ Project link not found for {clean_regnum}")
            continue

        # Switch to new tab
        wait.until(EC.number_of_windows_to_be(2))
        new_tab = [tab for tab in driver.window_handles if tab != driver.current_window_handle][0]
        driver.switch_to.window(new_tab)

        # Wait for page to load
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(2)  # Slight pause for heavy pages

        try:
            # Extract table
            table = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="GV_Building"]')))
            rows = table.find_elements(By.TAG_NAME, 'tr')

            # Open output CSV
            with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header if file is new
                if csvfile.tell() == 0:
                    headers = ['Reg. No'] + [header.text.strip() for header in rows[0].find_elements(By.TAG_NAME, 'th')]
                    writer.writerow(headers)

                # Write data rows
                for row in rows[1:]:
                    cells = [regnum] + [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, 'td')]
                    writer.writerow(cells)

                print(f"✅ Data saved for {clean_regnum}")

        except Exception as e:
            print(f"⚠️ Table not found for {clean_regnum}: {e}")

        # Close the tab and return to main window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    except Exception as e:
        print(f"❗ Error processing {regnum}: {e}")
        try:
            driver.quit()
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            wait = WebDriverWait(driver, 15)
            driver.get('https://rera.bihar.gov.in/RegisteredPP.aspx')
        except Exception as e2:
            print(f"❗ Failed to restart browser: {e2}")
            break  # If can't even restart, break the loop

# --- Done ---

driver.quit()
print("\n✅ All done!")
