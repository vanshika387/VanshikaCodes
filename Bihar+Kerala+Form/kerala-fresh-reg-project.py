from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Step 1: Setup the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Step 2: Open the webpage
url = "https://reraonline.kerala.gov.in/SearchList/Search"  # Replace with your desired URL
driver.get(url)

# Step 3: Wait for the page to load
time.sleep(3)  # You can also use WebDriverWait for more efficient waiting

def completed():
    driver.find_element(By.CSS_SELECTOR, "input[type='radio'][value='Completed']").click()
    driver.find_element(By.ID, "btnSearch").click() 

    time.sleep(10)  # Wait for the page to load     
     
    # Step 6: Iterate through each row and extract column data
    page_number = 0  # Track page number for writing headers only once
    previous_page_content = None  # Track content of the previous page
    headers = []  # To store table headers

    while True:
        # Step 6: Locate the table and extract rows
        table = driver.find_element(By.TAG_NAME, 'table')
        rows = table.find_elements(By.TAG_NAME, 'tr')

        # Step 7: Extract table headers (only on the first page)
        if page_number == 0:
            header_row = rows[0]  # Assuming first row contains headers
            header_columns = header_row.find_elements(By.TAG_NAME, 'th')
            headers = [header.text for header in header_columns[:-4]]  # Exclude last two columns
            print("Headers:", headers)

        # Step 8: Extract table data (excluding last two columns)
        table_data = []
        for row in rows[1:]:  # Start from the second row to skip headers
            columns = row.find_elements(By.TAG_NAME, 'td')
            if columns:
                row_data = [col.text for col in columns[:-4]]  # Exclude last two columns
                table_data.append(row_data)
        
        # Step 9: Write the page data to CSV immediately after extracting it
        df = pd.DataFrame(table_data, columns=headers if page_number == 0 else None)
        
        # Define the CSV file name
        csv_file = 'kerala-completed-projects.csv'
        
        # If it's the first page, write the header; otherwise, skip it
        if page_number == 0:
            df.to_csv(csv_file, mode='w', index=False, header=True)
        else:
            df.to_csv(csv_file, mode='a', index=False, header=False)
        
        print(f"Page {page_number + 1} data written to CSV.")
        page_number += 1
        
        # Check if the content is the same as the previous page
        current_page_content = [item for sublist in table_data for item in sublist]
        if current_page_content == previous_page_content:
            print("Same content as previous page detected. Ending pagination.")
            break
        previous_page_content = current_page_content
                 
        # Step 10: Try to locate and click the "Next" button
        try:
            # Locate the "Next" button
            next_button = driver.find_element(By.ID, 'btnNext')  

            # Check if the "Next" button is disabled or not clickable
            if next_button.get_attribute('disabled') == 'disabled' or not next_button.is_enabled():
                print("Next button is disabled or not clickable. Ending pagination.")
                break

            # If not disabled, click the "Next" button to proceed to the next page
            next_button.click()

            # Retry mechanism to wait for the table to load after clicking "Next"
            retries = 0
            max_retries = 10
            table_loaded = False

            while retries < max_retries:
                try:
                    # Wait for the table to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'table'))
                    )
                    table_loaded = True
                    break  # Break out of the retry loop if table is loaded
                except:
                    retries += 1
                    print(f"Retry {retries}/{max_retries}: Reloading page...")
                    driver.refresh()
                    time.sleep(2)  # Adjust as necessary

            if not table_loaded:
                print("Table did not load after 10 retries. Exiting.")
                break

        except Exception as e:
            # If there's an issue (e.g., no "Next" button), break the loop
            print("Error or no more pages:", e)
            break

    # Step 11: Close the WebDriver
    driver.quit()

completed()
