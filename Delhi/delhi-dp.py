from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome()

# URL of the promoter list page
promoter_list_url = "https://rera.delhi.gov.in/registered_promoters_list"  # Replace with the actual URL
driver.get(promoter_list_url)

wait = WebDriverWait(driver, 10)  # Explicit wait

# Extract promoter details and navigate to project details
promoter_data = []  # To store all extracted data

# Iterate through promoter rows
rows = driver.find_elements(By.XPATH, "//tr[contains(@class, 'even') or contains(@class, 'odd')]")
for row in rows:
    try:
        # Extract promoter details
        name = row.find_element(By.XPATH, ".//strong[contains(text(), 'Name')]/following-sibling::text()").strip()
        address = row.find_element(By.XPATH, ".//strong[contains(text(), 'Address')]/following-sibling::text()").strip()
        email = row.find_element(By.XPATH, ".//strong[contains(text(), 'Email')]/following-sibling::text()").strip()
        phone = row.find_element(By.XPATH, ".//strong[contains(text(), 'Phone Number')]/following-sibling::text()").strip()
        
        # Click "View Project" to navigate to the project details page
        project_link = row.find_element(By.XPATH, ".//a[contains(@class, 'product_list') and contains(@href, 'project_page')]")
        project_href = project_link.get_attribute("href")
        driver.execute_script("window.open(arguments[0]);", project_href)
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the new tab
        
        # Wait for the project details page to load
        time.sleep(3)  # You can use WebDriverWait here if needed

        # Extract project details using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Extract project details
        name_label = soup.find("span", text=" Name :")
        project_name = name_label.find_parent("div").find_next_sibling("div").text.strip() if name_label else "Not Found"
        
        location_label = soup.find("span", text=" Location :")
        location = location_label.find_parent("div").find_next_sibling("div").text.strip() if location_label else "Not Found"
        
        latitude_label = soup.find("span", text=" Latitude :")
        latitude = latitude_label.find_parent("div").find_next_sibling("div").text.strip() if latitude_label else "Not Found"
        
        longitude_label = soup.find("span", text=" Longitude :")
        longitude = longitude_label.find_parent("div").find_next_sibling("div").text.strip() if longitude_label else "Not Found"
        
        # Save data
        promoter_data.append({
            "Promoter Name": name,
            "Address": address,
            "Email": email,
            "Phone": phone,
            "Project Name": project_name,
            "Project Location": location,
            "Latitude": latitude,
            "Longitude": longitude,
        })

        # Close the project details tab and switch back to the main tab
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
    except Exception as e:
        print(f"Error processing row: {e}")
        continue

# Print all extracted data
for data in promoter_data:
    print(data)

# Close the driver
driver.quit()
