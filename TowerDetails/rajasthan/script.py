import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Setup
driver = webdriver.Chrome()
driver.get("https://rera.rajasthan.gov.in/ProjectSearch?Out=Y")
wait = WebDriverWait(driver, 10)

# Function to get or create the CSV writer
def get_csv_writer():
    file = open('apartment_details.csv', mode='a', newline='', encoding='utf-8')
    writer = csv.writer(file)
    # Check if file is empty (new file)
    file.seek(0, 2)  # Go to end of file
    is_new_file = file.tell() == 0  # True if file is empty
    return writer, file, is_new_file

# Read CSV without pandas
with open('focus.csv', mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    
    for row in csv_reader:
        xid = row['XID'].strip()  # Get the XID
        reg_no = row['Reg.'].strip()  # Get the Reg. number
        if not reg_no:
            continue  # Skip if Reg. is empty

        try:
            # Input registration number
            cert_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="certificateNo"]')))
            cert_input.clear()
            cert_input.send_keys(reg_no)

            # Click search button
            search_btn = driver.find_element(By.ID, "btn_SearchProjectSubmit")
            search_btn.click()

            # Wait for results
            time.sleep(2)  # Small wait for search results to load

            # Try clicking on View button
            try:
                view_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn.btn-sm.btn-primary")))
                view_button.click()
            except TimeoutException:
                print(f"View button not found for Reg: {reg_no}, skipping.")
                continue  # Skip to next Reg if view button not found

            # Switch to new window
            driver.switch_to.window(driver.window_handles[1])

            # Find 'Updated project details' row and click the View link
            try:
                updated_project_row = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Updated project details')]"))
                )
                # Find the parent row and click the View link
                parent_row = updated_project_row.find_element(By.XPATH, './parent::tr')
                view_link = parent_row.find_element(By.TAG_NAME, 'a')
                view_link.click()

                # Switch to new window
                driver.switch_to.window(driver.window_handles[2])
                time.sleep(3)  # Wait for the new page to load

                # First find the APARTMENTS TYPE DETAILS section
                try:
                    # Find the parent container with APARTMENTS TYPE DETAILS
                    apartments_section = wait.until(EC.presence_of_element_located(
                        (By.XPATH, "//h3[contains(@class, 'TableHeading') and contains(text(), 'APARTMENTS TYPE DETAILS')]/parent::td")
                    ))
                    
                    # Within this section, find the "Sanctioned" heading and its table
                    sanctioned_header = apartments_section.find_element(By.XPATH, "./h3[text()='Sanctioned']")
                    sanctioned_table = sanctioned_header.find_element(By.XPATH, "following-sibling::table[1]")

                    # Extract headers from the "Sanctioned" table
                    header_row = sanctioned_table.find_element(By.XPATH, ".//thead/tr")
                    headers = [th.text.strip() for th in header_row.find_elements(By.TAG_NAME, 'th')]
                    headers.insert(0, 'XID')  # Add XID column
                    headers.insert(1, 'Registration Number')  # Add reg_no column

                    # Get the CSV writer and check if header needs to be written
                    csv_writer, csv_file, is_new_file = get_csv_writer()
                    
                    # Write header only for new file
                    if is_new_file:
                        csv_writer.writerow(headers)

                    # Extract data from the "Sanctioned" table
                    rows = sanctioned_table.find_elements(By.XPATH, ".//tbody/tr")
                    
                    for table_row in rows:
                        columns = table_row.find_elements(By.TAG_NAME, "td")
                        
                        # Extract data from each <td>
                        row_data = [column.text.strip() for column in columns]
                        
                        # Add the registration number to each row
                        row_data.insert(0, xid)
                        row_data.insert(1, reg_no)
                        
                        # Write the data to CSV file immediately
                        csv_writer.writerow(row_data)
                    
                    # Close the CSV file after writing data for this registration
                    csv_file.close()
                    print(f"Successfully extracted data for Reg: {reg_no}")
                
                except (TimeoutException, NoSuchElementException) as e:
                    print(f"Error finding apartment details table for Reg: {reg_no}")
                
                # Close the current window after extracting data
                driver.close()
                
                # Switch back to the second window
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                
                # Switch back to the main window
                driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"Error extracting apartment details for Reg: {reg_no}: {e}")
                
                # Close any extra windows and go back to main window
                while len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                
                continue

        except Exception as e:
            print(f"Error processing Reg: {reg_no}: {e}")
            
            # Ensure we get back to the main window
            while len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

# Finish
driver.quit()
print("Scraping completed. Data saved to apartment_details.csv")