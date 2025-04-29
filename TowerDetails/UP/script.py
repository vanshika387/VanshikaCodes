# import os
# import time
# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains

# # Setup driver
# driver = webdriver.Chrome()
# driver.maximize_window()

# # Open the website
# driver.get('https://up-rera.in/projects')

# # Open focus.csv manually
# with open('up/focus.csv', newline='', encoding='utf-8') as f:
#     reader = csv.DictReader(f)
#     focus_list = list(reader)

# # Prepare output CSV
# output_csv = 'up/output_apartments.csv'
# first_write = True

# # Open output CSV file for writing
# with open(output_csv, 'w', newline='', encoding='utf-8-sig') as out_csv:
#     writer = None  # We will initialize it after getting table headers

#     for row in focus_list:
#         xid = row['XID'].strip()
#         reg_number = row['Reg.'].strip()

#         try:
#             # Switch to window 0
#             driver.switch_to.window(driver.window_handles[0])
#             # driver.get('https://up-rera.in/projects')  # Refresh page cleanly
#             time.sleep(1)

#             # Enter reg number
#             search_input = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, '//*[@id="grdPojDetail"]/thead/tr[2]/td[4]/input'))
#             )
#             search_input.clear()
#             search_input.send_keys(reg_number)
#             time.sleep(1)

#             # Click search button
#             # Wait until anchor is clickable
#             # search_button = WebDriverWait(driver, 10).until(
#             #     EC.element_to_be_clickable((By.ID, 'anchorViewProject'))
#             # )

#             # # Scroll to the element (optional but safer)
#             # driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
#             # time.sleep(0.5)

#             link = driver.find_element(By.XPATH, '//*[@id="anchorViewProject"]')
#             href = link.get_attribute('href')
#             driver.execute_script(f"window.open('{href}', '_blank');")
#             # ActionChains(driver).move_to_element(link).click().perform()
#             # Now click it
#             # search_button.click()
#             time.sleep(3)


#             # Switch to window 1
#             WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
#             driver.switch_to.window(driver.window_handles[1])

#             # Click View Project Details button
#             view_project_button = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_pnlViewPrjDetail"]/a'))
#             )
#             view_project_button.click()
#             time.sleep(2)

#             # Switch to window 2
#             WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 2)
#             driver.switch_to.window(driver.window_handles[2])

#             # Wait until the page is fully loaded
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.TAG_NAME, 'body'))
#             )
#             time.sleep(6)

#             # Locate the table
#             table = driver.find_element(By.ID, 'ShowTableApartment')

#             # Extract table headers
#             headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]

#             # print("Length of Headers:", len(headers))

#             # if len(headers) == 12:
#             #     csv_file1 = 'apartment_data.csv'
#             # else:
#             #     csv_file1 = 'others_data.csv'

#             csv_file1 = 'apartment_data.csv'
#             # Add "Registration Number" as the first header
#             headers.insert(0, "Registration Number")

#             # Extract table rows
#             rows = table.find_elements(By.TAG_NAME, 'tr')

#             # Prepare the data
#             data_1 = []
#             for row in rows[1:]:  # Skip the header row
#                 cells = row.find_elements(By.TAG_NAME, 'td')
#                 row_data = [xid] + [cell.text for cell in cells]
#                 data_1.append(row_data)

#             # Save data to CSV
#             file_exists1 = os.path.isfile(csv_file1)
#             with open(csv_file1, mode='a', newline='') as file:
#                 writer = csv.writer(file)
#                 if not file_exists1:  # Write header only if the file doesn't exist
#                     writer.writerow(headers)
#                 writer.writerows(data_1)  # Write rows

#             print(f"Data saved to {csv_file1}")

#             # df = pd.DataFrame([data])
#             # print(data)

#             # # Find the table
#             # table = WebDriverWait(driver, 10).until(
#             #     EC.presence_of_element_located((By.ID, 'ShowTableApartment'))
#             # )

#             # # Extract table header
#             # headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]

#             # # Add "Registration Number" as the first header
#             # headers.insert(0, "Registration Number")

#             # # Extract table rows
#             # rows = table.find_elements(By.TAG_NAME, 'tr')

#             # # Prepare the data
#             # data_1 = []
#             # for row in rows[1:]:  # Skip the header row
#             #     cells = row.find_elements(By.TAG_NAME, 'td')
#             #     row_data = [reg_number] + [cell.text.strip() for cell in cells]
#             #     data_1.append(row_data)

#             # # Save data to CSV
#             # file_exists1 = os.path.isfile(output_csv)
#             # with open(output_csv, mode='a', newline='', encoding='utf-8-sig') as file:
#             #     writer = csv.writer(file)
#             #     if not file_exists1:  # Write header only if the file doesn't exist
#             #         writer.writerow(headers)
#             #     writer.writerows(data_1)  # Write rows

#             # print(f"Processed: {reg_number}")

#         except Exception as e:
#             print(f"Error processing {reg_number}: {e}")

#         finally:
#             # Close window 2 and window 1 if open
#             if len(driver.window_handles) > 2:
#                 driver.switch_to.window(driver.window_handles[2])
#                 driver.close()
#             if len(driver.window_handles) > 1:
#                 driver.switch_to.window(driver.window_handles[1])
#                 driver.close()
#             driver.switch_to.window(driver.window_handles[0])

# # Final cleanup
# driver.quit()

import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# Setup driver
driver = webdriver.Chrome()
driver.maximize_window()

# Open the website
driver.get('https://up-rera.in/projects')

# Open focus.csv manually
with open('up/focus.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    focus_list = list(reader)

# Prepare output CSV
output_csv = 'up/output_apartments.csv'
first_write = True

# Open output CSV file for writing
with open(output_csv, 'w', newline='', encoding='utf-8-sig') as out_csv:
    writer = None  # We will initialize it after getting table headers

    for row in focus_list:
        xid = row['XID'].strip()
        reg_number = row['Reg.'].strip()

        try:
            # Switch to window 0
            driver.switch_to.window(driver.window_handles[0])
            # driver.get('https://up-rera.in/projects')  # Refresh page cleanly
            time.sleep(1)

            # Enter reg number
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="grdPojDetail"]/thead/tr[2]/td[4]/input'))
            )
            search_input.clear()
            search_input.send_keys(reg_number)
            time.sleep(1)

            # Click search button
            # Wait until anchor is clickable
            # search_button = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.ID, 'anchorViewProject'))
            # )

            # # Scroll to the element (optional but safer)
            # driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
            # time.sleep(0.5)

            # Find all elements with ID 'anchorViewProject'
            links = driver.find_elements(By.ID, 'anchorViewProject')

            # Filter only the ones that are visible
            visible_links = [link for link in links if link.is_displayed()]

            if not visible_links:
                raise Exception("No visible 'anchorViewProject' link found.")

            # Click the first visible one (or get href and open)
            href = visible_links[0].get_attribute('href')
            driver.execute_script(f"window.open('{href}', '_blank');")
            time.sleep(3)



            # Switch to window 1
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
            driver.switch_to.window(driver.window_handles[1])

            rerano = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_lblregno').text
            if rerano != reg_number:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            # Click View Project Details button
            view_project_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_pnlViewPrjDetail"]/a'))
            )
            view_project_button.click()
            time.sleep(2)

            # Switch to window 2
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 2)
            driver.switch_to.window(driver.window_handles[2])

            # Wait until the page is fully loaded
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            time.sleep(5)
            
            # *** NEW CODE: Scroll through the entire page ***
            # try:
            #     # Get the initial page height
            #     last_height = driver.execute_script("return document.body.scrollHeight")
                
            #     # Scroll in increments
            #     for i in range(0, last_height, 200):  # Scroll in steps of 200px
            #         driver.execute_script(f"window.scrollTo(0, {i});")
            #         time.sleep(0.3)  # Small delay to allow content to load
                
            #     # Scroll back to top
            #     driver.execute_script("window.scrollTo(0, 0);")
                
            #     # Scroll down again slowly to ensure everything is loaded
            #     current_height = 0
            #     while current_height < last_height:
            #         current_height += 300
            #         driver.execute_script(f"window.scrollTo(0, {current_height});")
            #         time.sleep(0.5)
                
            #     # Wait a bit after scrolling to ensure everything has loaded
            #     time.sleep(3)
                
            # except Exception as e:
            #     print(f"Error during scrolling for {reg_number}: {e}")
            # *** END NEW CODE ***
            # time.sleep(10)

            # Locate the table
            table = driver.find_element(By.ID, 'ShowTableApartment')

            # Extract table headers
            headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]

            # print("Length of Headers:", len(headers))

            # if len(headers) == 12:
            #     csv_file1 = 'apartment_data.csv'
            # else:
            #     csv_file1 = 'others_data.csv'

            csv_file1 = 'up/buildindDetails.csv'
            # Add "Registration Number" as the first header
            headers.insert(0, "Registration Number")
            headers.insert(1, "XID")

            # Extract table rows
            rows = table.find_elements(By.TAG_NAME, 'tr')

            # Prepare the data
            data_1 = []
            for row in rows[1:]:  # Skip the header row
                cells = row.find_elements(By.TAG_NAME, 'td')
                row_data = [xid] + [reg_number] + [cell.text for cell in cells]
                data_1.append(row_data)

            # Save data to CSV
            file_exists1 = os.path.isfile(csv_file1)
            with open(csv_file1, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists1:  # Write header only if the file doesn't exist
                    writer.writerow(headers)
                writer.writerows(data_1)  # Write rows

            print(f"Data saved to {csv_file1}")

            # df = pd.DataFrame([data])
            # print(data)

            # # Find the table
            # table = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, 'ShowTableApartment'))
            # )

            # # Extract table header
            # headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]

            # # Add "Registration Number" as the first header
            # headers.insert(0, "Registration Number")

            # # Extract table rows
            # rows = table.find_elements(By.TAG_NAME, 'tr')

            # # Prepare the data
            # data_1 = []
            # for row in rows[1:]:  # Skip the header row
            #     cells = row.find_elements(By.TAG_NAME, 'td')
            #     row_data = [reg_number] + [cell.text.strip() for cell in cells]
            #     data_1.append(row_data)

            # # Save data to CSV
            # file_exists1 = os.path.isfile(output_csv)
            # with open(output_csv, mode='a', newline='', encoding='utf-8-sig') as file:
            #     writer = csv.writer(file)
            #     if not file_exists1:  # Write header only if the file doesn't exist
            #         writer.writerow(headers)
            #     writer.writerows(data_1)  # Write rows

            # print(f"Processed: {reg_number}")

        except Exception as e:
            print(f"Error processing {reg_number}: {e}")

        finally:
            # Close window 2 and window 1 if open
            if len(driver.window_handles) > 2:
                driver.switch_to.window(driver.window_handles[2])
                driver.close()
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

# Final cleanup
driver.quit()