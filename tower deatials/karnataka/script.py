# import time
# import csv
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException

# # Setup Selenium WebDriver (assuming chromedriver is in PATH)
# driver = webdriver.Chrome()
# wait = WebDriverWait(driver, 10)

# # Create output directory if it doesn't exist
# output_dir = "rera_data"
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# # Open website
# driver.get('https://rera.karnataka.gov.in/viewAllProjects')
# driver.maximize_window()

# # Open and read CSV
# with open('karnataka/focus.csv', newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile, delimiter=',')
#     for row in reader:
#         reg_no = row['Reg.'].strip()
#         print(f"Processing registration number: {reg_no}")
        
#         # Find registration number field and enter reg_no
#         search_input = wait.until(EC.presence_of_element_located((By.ID, 'regNo2')))
#         search_input.clear()
#         search_input.send_keys(reg_no)

#         time.sleep(2)  # Wait for a moment to ensure the input is registered
        
#         # Click Search button
#         search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-style')))
#         driver.execute_script("arguments[0].click();", search_button)

#         time.sleep(5)  # Wait for search results to load
        
#         try:
#             # Click "View Project Details" button
#             view_details_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-md')))
#             driver.execute_script("arguments[0].click();", view_details_button)
            
#             # Click "Project Details" tab
#             proj_details_tab = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Project Details')))
#             driver.execute_script("arguments[0].click();", proj_details_tab)
            
#             # Wait for page to load
#             time.sleep(10)
            
#             try:
#                 # Find the div containing the specified h1 element
#                 target_text = "Development Details ( Bifurcation of Type of Inventories/Flats/Villas )"
#                 # Find the h1 element first
#                 h1_elements = driver.find_elements(By.TAG_NAME, "h1")
#                 target_div = None
                
#                 for h1 in h1_elements:
#                     if "Development Details" in h1.text and "Bifurcation of Type of Inventories" in h1.text:
#                         # Found the heading, now find its parent div
#                         target_div = h1.find_element(By.XPATH, "./..")
#                         break
                
#                 if target_div:
#                     # Find all tables within this div
#                     tables = target_div.find_elements(By.TAG_NAME, "table")
                    
#                     if tables:
#                         print(f"Found {len(tables)} tables for {reg_no}")
                        
#                         # Create a CSV file for this registration number
#                         with open(f"{output_dir}/{reg_no}_development_details.csv", 'w', newline='', encoding='utf-8') as csvfile:
#                             csv_writer = csv.writer(csvfile)
                            
#                             # Process each table
#                             for table_index, table in enumerate(tables):
#                                 # Add table separator if not the first table
#                                 if table_index > 0:
#                                     csv_writer.writerow([])
#                                     csv_writer.writerow([f"Table {table_index + 1}"])
#                                     csv_writer.writerow([])
#                                 else:
#                                     csv_writer.writerow([f"Table {table_index + 1}"])
#                                     csv_writer.writerow([])
                                
#                                 # Get table headers
#                                 headers = []
#                                 header_cells = table.find_elements(By.TAG_NAME, "th")
#                                 if header_cells:
#                                     headers = [cell.text.strip() for cell in header_cells]
#                                 else:
#                                     # If no th elements, try first row as headers
#                                     first_row = table.find_elements(By.XPATH, ".//tr[1]/td")
#                                     headers = [cell.text.strip() for cell in first_row]
                                
#                                 # Write headers
#                                 csv_writer.writerow(headers)
                                
#                                 # Get table rows (skip header row if it used th elements)
#                                 rows = table.find_elements(By.TAG_NAME, "tr")
#                                 start_row = 1 if header_cells else 2  # Skip header row(s)
                                
#                                 for row in rows[start_row:]:
#                                     cells = row.find_elements(By.TAG_NAME, "td")
#                                     row_data = [cell.text.strip() for cell in cells]
#                                     if any(row_data):  # Only write non-empty rows
#                                         csv_writer.writerow(row_data)
#                     else:
#                         print(f"No tables found for {reg_no}")
#                 else:
#                     print(f"Development Details heading not found for {reg_no}")
                    
#             except Exception as e:
#                 print(f"Error extracting tables for {reg_no}: {e}")
                
#             # Go back to search page
#             # driver.back()
#             driver.back()
            
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Error processing {reg_no}: {e}")
#             # Try to go back to the search page
#             try:
#                 driver.get('https://rera.karnataka.gov.in/viewAllProjects')
#             except:
#                 print("Error navigating back to search page. Reloading...")
#                 driver.get('https://rera.karnataka.gov.in/viewAllProjects')
                
#         # Add a pause between records to avoid overloading the server
#         time.sleep(2)

# # Close the driver after processing
# driver.quit()

# print("Processing complete. Results saved in the 'rera_data' directory.")

# import time
# import csv
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, TimeoutException

# # Setup Selenium WebDriver (assuming chromedriver is in PATH)
# driver = webdriver.Chrome()
# wait = WebDriverWait(driver, 10)

# # Create output directory if it doesn't exist
# output_dir = "rera_data"
# if not os.path.exists(output_dir):
#     os.makedirs(output_dir)

# # Open website
# driver.get('https://rera.karnataka.gov.in/viewAllProjects')
# driver.maximize_window()

# # Open and read CSV
# with open('karnataka/focus.csv', newline='', encoding='utf-8') as csvfile:
#     reader = csv.DictReader(csvfile, delimiter=',')
#     for row in reader:
#         reg_no = row['Reg.'].strip()
#         print(f"Processing registration number: {reg_no}")
        
#         # Create a safe filename by replacing slashes with underscores
#         safe_filename = reg_no.replace('/', '_')
        
#         # Find registration number field and enter reg_no
#         search_input = wait.until(EC.presence_of_element_located((By.ID, 'regNo2')))
#         search_input.clear()
#         search_input.send_keys(reg_no)

#         time.sleep(2)  # Wait for a moment to ensure the input is registered
        
#         # Click Search button
#         search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-style')))
#         driver.execute_script("arguments[0].click();", search_button)

#         time.sleep(5)  # Wait for search results to load
        
#         try:
#             # Click "View Project Details" button
#             view_details_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-md')))
#             driver.execute_script("arguments[0].click();", view_details_button)
            
#             # Click "Project Details" tab
#             proj_details_tab = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Project Details')))
#             driver.execute_script("arguments[0].click();", proj_details_tab)
            
#             # Wait for page to load
#             time.sleep(10)
            
#             try:
#                 # Find the div containing the specified h1 element
#                 target_text = "Development Details ( Bifurcation of Type of Inventories/Flats/Villas )"
#                 # Find the h1 element first
#                 h1_elements = driver.find_elements(By.TAG_NAME, "h1")
#                 target_div = None
                
#                 for h1 in h1_elements:
#                     if "Development Details" in h1.text and "Bifurcation of Type of Inventories" in h1.text:
#                         # Found the heading, now find its parent div
#                         target_div = h1.find_element(By.XPATH, "./..")
#                         break
                
#                 if target_div:
#                     # Find all tables within this div
#                     tables = target_div.find_elements(By.TAG_NAME, "table")
                    
#                     if tables:
#                         print(f"Found {len(tables)} tables for {reg_no}")
                        
#                         # Create a CSV file for this registration number using the safe filename
#                         with open(f"{output_dir}/{safe_filename}_development_details.csv", 'w', newline='', encoding='utf-8') as csvfile:
#                             csv_writer = csv.writer(csvfile)
                            
#                             # Process each table
#                             for table_index, table in enumerate(tables):
#                                 # Add table separator if not the first table
#                                 if table_index > 0:
#                                     csv_writer.writerow([])
#                                     csv_writer.writerow([f"Table {table_index + 1}"])
#                                     csv_writer.writerow([])
#                                 else:
#                                     csv_writer.writerow([f"Table {table_index + 1}"])
#                                     csv_writer.writerow([])
                                
#                                 # Get table headers
#                                 headers = []
#                                 header_cells = table.find_elements(By.TAG_NAME, "th")
#                                 if header_cells:
#                                     headers = [cell.text.strip() for cell in header_cells]
#                                 else:
#                                     # If no th elements, try first row as headers
#                                     first_row = table.find_elements(By.XPATH, ".//tr[1]/td")
#                                     headers = [cell.text.strip() for cell in first_row]
                                
#                                 # Write headers
#                                 csv_writer.writerow(headers)
                                
#                                 # Get table rows (skip header row if it used th elements)
#                                 rows = table.find_elements(By.TAG_NAME, "tr")
#                                 start_row = 1 if header_cells else 2  # Skip header row(s)
                                
#                                 for row in rows[start_row:]:
#                                     cells = row.find_elements(By.TAG_NAME, "td")
#                                     row_data = [cell.text.strip() for cell in cells]
#                                     if any(row_data):  # Only write non-empty rows
#                                         csv_writer.writerow(row_data)
#                     else:
#                         print(f"No tables found for {reg_no}")
#                 else:
#                     print(f"Development Details heading not found for {reg_no}")
                    
#             except Exception as e:
#                 print(f"Error extracting tables for {reg_no}: {e}")
                
#             # Go back to search page
#             # driver.back()
#             driver.back()
            
#         except (NoSuchElementException, TimeoutException) as e:
#             print(f"Error processing {reg_no}: {e}")
#             # Try to go back to the search page
#             try:
#                 driver.get('https://rera.karnataka.gov.in/viewAllProjects')
#             except:
#                 print("Error navigating back to search page. Reloading...")
#                 driver.get('https://rera.karnataka.gov.in/viewAllProjects')
                
#         # Add a pause between records to avoid overloading the server
#         time.sleep(2)

# # Close the driver after processing
# driver.quit()

# print("Processing complete. Results saved in the 'rera_data' directory.")

import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Setup Selenium WebDriver (assuming chromedriver is in PATH)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

# Create output directory if it doesn't exist
output_dir = "Karnataka"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a single CSV file for all records
output_file = f"{output_dir}/Karnatak_all_development_details2.csv"

# Open website
driver.get('https://rera.karnataka.gov.in/viewAllProjects')
driver.maximize_window()
cnt = 0

# Open and read CSV
with open('karnataka/focus2.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',')
    for row in reader:
        cnt += 1
        # xid = row['XID'].strip()
        reg_no = row['reg'].strip()
        print(f"Processing registration number {cnt}: {reg_no}")
        
        # Find registration number field and enter reg_no
        search_input = wait.until(EC.presence_of_element_located((By.ID, 'regNo2')))
        search_input.clear()
        search_input.send_keys(reg_no)

        time.sleep(2)  # Wait for a moment to ensure the input is registered
        
        # Click Search button
        search_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-style')))
        driver.execute_script("arguments[0].click();", search_button)

        time.sleep(5)  # Wait for search results to load
        
        try:
            # Click "View Project Details" button
            view_details_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-md')))
            driver.execute_script("arguments[0].click();", view_details_button)
            
            # Click "Project Details" tab
            proj_details_tab = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Project Details')))
            driver.execute_script("arguments[0].click();", proj_details_tab)
            
            # Wait for page to load
            time.sleep(10)

            # Initialize data for this project
            project_details = {'RegNo': reg_no, 'FAR Sanctioned': '', 'Number of Towers': ''}

            fields_to_find = ["FAR Sanctioned", "Number of Towers"]
            for field in fields_to_find:
                try:
                    label_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, f'//p[contains(text(), "{field}")]'))
                    )
                    parent_div = label_element.find_element(By.XPATH, '..')
                    value_div = parent_div.find_element(By.XPATH, 'following-sibling::div')
                    value_text = value_div.text.strip()
                    project_details[field] = value_text
                except Exception as e:
                    print(f"Field '{field}' not found for RegNo {reg_no}: {e}")
            
            try:
                # Find the div containing the specified h1 element
                target_text = "Development Details ( Bifurcation of Type of Inventories/Flats/Villas )"
                # Find the h1 element first
                h1_elements = driver.find_elements(By.TAG_NAME, "h1")
                target_div = None
                
                for h1 in h1_elements:
                    if "Development Details" in h1.text and "Bifurcation of Type of Inventories" in h1.text:
                        # Found the heading, now find its parent div
                        target_div = h1.find_element(By.XPATH, "./..")
                        break
                
                if target_div:
                    # Find all tables within this div
                    tables = target_div.find_elements(By.TAG_NAME, "table")
                    
                    if tables:
                        print(f"Found {len(tables)} tables for {reg_no}")
                        
                        # Open the single CSV file in append mode
                        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                            csv_writer = csv.writer(csvfile)
                            
                            # Add a record separator and registration number identifier
                            csv_writer.writerow([])
                            csv_writer.writerow(["Registration Number:", reg_no])
                            csv_writer.writerow([project_details])
                            csv_writer.writerow([])
                            
                            # Process each table
                            for table_index, table in enumerate(tables):
                                # Add table separator
                                csv_writer.writerow([f"Table {table_index + 1}"])
                                csv_writer.writerow([])
                                
                                # # Get table headers
                                # headers = []
                                # header_cells = table.find_elements(By.TAG_NAME, "th")
                                # if header_cells:
                                #     headers = [cell.text.strip() for cell in header_cells]
                                # else:
                                #     # If no th elements, try first row as headers
                                #     first_row = table.find_elements(By.XPATH, ".//tr[1]/td")
                                #     headers = [cell.text.strip() for cell in first_row]
                                
                                # # Prepend "Reg_No" to headers to include the identifier in each row
                                # modified_headers = ["XID"] + ["Reg_No"] + headers
                                # csv_writer.writerow(modified_headers)
                                
                                # # Get table rows (skip header row if it used th elements)
                                rows = table.find_elements(By.TAG_NAME, "tr")
                                # start_row = 0 if header_cells else 0  # Skip header row(s)
                                start_row = 0
                                
                                for row in rows[start_row:]:
                                    cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(By.TAG_NAME, "th")
                                    row_data = [cell.text.strip() for cell in cells]
                                    if any(row_data):  # Only write non-empty rows
                                        # Prepend registration number to each row
                                        csv_writer.writerow([reg_no] + row_data)
                    else:
                        print(f"No tables found for {reg_no}")
                        # No data will be written to the CSV
                else:
                    print(f"Development Details heading not found for {reg_no}")
                    # No data will be written to the CSV
                    
            except Exception as e:
                print(f"Error extracting tables for {reg_no}: {e}")
                # No error message will be written to the CSV
                
            # Go back to search page
            driver.back()
            
        except (NoSuchElementException, TimeoutException) as e:
            print(f"Error processing {reg_no}: {e}")
            # No error message will be written to the CSV
            
            # Try to go back to the search page
            try:
                driver.get('https://rera.karnataka.gov.in/viewAllProjects')
            except:
                print("Error navigating back to search page. Reloading...")
                driver.get('https://rera.karnataka.gov.in/viewAllProjects')
                
        # Add a pause between records to avoid overloading the server
        time.sleep(2)

# Close the driver after processing
driver.quit()

print("Processing complete. Results saved in 'rera_data/all_development_details.csv'.")
