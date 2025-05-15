from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time

# Set up Selenium WebDriver
driver = webdriver.Chrome()  # Ensure chromedriver is in PATH
driver.get("https://reraonline.kerala.gov.in/SearchList/Search#")

# Click on "Advanced Search"
advanced_search = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.LINK_TEXT, "Advance Search"))
)
advanced_search.click()

# List to store extracted data
all_data = []

# Function to reinitialize the district dropdown after refreshing the page
def get_district_dropdown():
    district_dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'District'))
    )
    return Select(district_dropdown)

# Get the dropdown options
select = get_district_dropdown()

# Iterate through each district option
for option in select.options:
    district_name = option.text.strip()
    
    if district_name.lower() == "select district":  # Skip default option
        continue

    print(f"Processing district: {district_name}")

    # Select the district
    select.select_by_visible_text(district_name)
    time.sleep(1)  # Give time for UI to update

    # Click Search button
    search_button = driver.find_element(By.XPATH, '//*[@id="btnSearch"]')
    search_button.click()

    # Wait for results to load
    time.sleep(3)

    try:
        # Locate table with Project Details
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        print(f"Table found for {district_name}")

        # Pagination loop
        while True:
            # Get all rows except header
            rows = table.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) >= 3:
                    project_name = columns[0].text.strip()
                    promoter_name = columns[1].text.strip()
                    certificate_no = columns[2].text.strip()

                    all_data.append([district_name, project_name, promoter_name, certificate_no])

            # Check if there is a next page **after processing all rows**
            try:
                next_page = driver.find_element(By.ID, "btnNext")  # Locate Next button
                if next_page.get_attribute("disabled"):
                    break  # Exit pagination loop if disabled
                next_page.click()
                time.sleep(2)  # Allow new page to load
            except:
                # Exit pagination loop if "Next" button is not found
                break

        # Click on "Advanced Search" again to reset the search
        advanced_search = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Advance Search"))
        )
        advanced_search.click()
        time.sleep(3)  # Allow time for the page to be ready

        # **Reinitialize the dropdown** after refreshing the page
        select = get_district_dropdown()

    except Exception as e:
        print(f"No results for {district_name}: {e}")

# Close the driver
driver.quit()

# Save data to CSV
df = pd.DataFrame(all_data, columns=["District", "Project Name", "Promoter Name", "Certificate No."])
df.to_csv("rera_kerala_projects.csv", index=False)
print("Data saved to rera_kerala_projects.csv")
