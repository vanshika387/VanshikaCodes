from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
 
 
driver = webdriver.Chrome()
 
 
url = "https://maharera.maharashtra.gov.in/projects-search-result?project_name=&project_location=&project_completion_date=&project_state=27&project_district=Array&carpetAreas=&completionPercentages=&project_division=&page=2225&op=Search"   
 
driver.get(url)
start_time = time.time()
 
# Step 3: Wait for the page to load (adjust the time as necessary)
time.sleep(3)  # You can also use WebDriverWait for more efficient waiting
 
# Step 6: Iterate through each row and extract column data
all_data = []
page_number = 2225  # Track page number
while True:
    print(f"Processing page {page_number}")
    # Step 6: Locate the table and extract rows
    retries = 3
    attempt = 0
    while attempt < retries:
        try:
            rows = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#content > div > div.row > div.col-md-9.fullShow.col-lg-12 > div.container > div'))
            )
            print("Divs loaded successfully!")
            break  # Successfully loaded, exit retry loop
        except:
            attempt += 1
            print(f"Retrying... attempt {attempt}")
            time.sleep(3)  # Wait before retrying
 
    # Extract data from each row
    for row in rows:
        cells = row.find_elements(By.XPATH, "div[1]/p[1]")  # Find all cells within the current row
        row_data = [cell.text for cell in cells]  # Extract text from each cell
        print(row_data)
        all_data.append(row_data)  # Add the row's data to the list
 
    # Step 8: Write data to CSV before clicking next
    df = pd.DataFrame(all_data)
    df.to_csv('maharera-reg-no-only-data.csv', index=False)
    print(f"Data saved after page load. Total rows: {len(all_data)}")
 
    # Step 8: Try to locate and click the "Next" button
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
        )
        next_href = next_button.get_attribute("href")
        if not next_href:
            print("No more pages to navigate.")
            break
        driver.get(next_href)  # Navigate to the next page
        time.sleep(5)  # Wait for 5 seconds to allow the next page to load completely
        page_number += 1  # Increment page number
 
    except Exception as e:
        print("Error or no more pages:", e)
        break
 
end_time = time.time()
 
# Calculate the total crawl time
total_crawl_time = end_time - start_time
print(f"Total crawl time: {total_crawl_time:.2f} seconds")
 
# Step 8: Close the WebDriver
driver.quit()