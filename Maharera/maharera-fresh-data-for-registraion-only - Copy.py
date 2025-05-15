from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Step 1: Setup the WebDriver
driver = webdriver.Chrome()

# Step 2: Open the webpage
url = "https://maharera.maharashtra.gov.in/projects-search-result"  # Replace with your desired URL
driver.get(url)
start_time = time.time() 
# Step 3: Wait for the page to load (adjust the time as necessary)
time.sleep(3)  # You can also use WebDriverWait for more efficient waiting

page = 1

# Step 6: Iterate through each row and extract column data
all_data = []
while True:
    # Step 6: Locate the table and extract rows
     
    #rows = driver.find_elements(By.CSS_SELECTOR, '#content > div > div.row > div.col-md-9.fullShow.col-lg-12 > div.container > div')
    
    try:
    # Wait for the div with class 'row' to be present (replace with the actual class, id, or XPath)
        rows = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#content > div > div.row > div.col-md-9.fullShow.col-lg-12 > div.container > div'))
        )
        print("Divs loaded successfully!")
    except:
        print("Timeout: The div elements did not load in time!")
    for row in rows:
        cells = row.find_elements(By.XPATH, "div[1]/p[1]")  # Find all cells within the current row
        row_data = [cell.text for cell in cells]  # Extract text from each cell
        print(row_data)
        all_data.append(row_data)  # Add the row's data to the list
         
    
    # Step 8: Try to locate and click the "Next" button
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.next"))
        )
        page += 1
        print(f"Page {page} loaded successfully!")
        if (page % 1000) == 0:
            time.sleep(180)
       
        next_href = next_button.get_attribute("href")
        if not next_href:
            print("No more pages to navigate.")
            break
 
        driver.get(next_href)  # Navigate to the next page
 
    except Exception as e:
        print("Error or no more pages:", e)
        break
end_time = time.time()

# Calculate the total crawl time
total_crawl_time = end_time - start_time
print(f"Total crawl time: {total_crawl_time:.2f} seconds")

# Step 8: Close the WebDriver

df = pd.DataFrame(all_data)
df.to_csv('maharera-reg-no-only-data-2.csv',mode='a', index=False)
