# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import pandas as pd
# import time

# # Configurations (Update these)
# CSV_FILE = "up_project_details.csv"  # Replace with your actual CSV file
# LOGIN_URL = "https://xidbackend.99acres.com/index.php/mainpage/login"  # Replace with your login page URL
# USERNAME = "backend.ops"  # Replace with your actual username
# PASSWORD = "123456"  # Replace with your actual password
# NEW_PROJECT_XPATH = "/html/body/table[2]/tbody/tr[3]/td[1]/table/tbody/tr[5]/td/a"  # Update based on actual hyperlink text

# # Load CSV data
# df = pd.read_csv(CSV_FILE)

# # Setup Selenium WebDriver (Ignore SSL errors)
# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument("--ignore-certificate-errors")  # Bypass SSL warning
# driver = webdriver.Chrome(options=chrome_options)

# # Step 1: Open Login Page
# driver.get(LOGIN_URL)
# time.sleep(2)  # Allow page to load

# # Step 2: Enter Username & Password
# driver.find_element(By.NAME, "username").send_keys(USERNAME)  # Update input field name if needed
# driver.find_element(By.NAME, "password").send_keys(PASSWORD)  # Update input field name if needed
# driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)  # Press Enter to log in
# time.sleep(3)  # Wait for navigation

# # Step 3: Click "Enter a New Project" Hyperlink
# try:
#     new_project_link = driver.find_element(By.XPATH, NEW_PROJECT_XPATH)
#     new_project_link.click()
#     time.sleep(2)  # Wait for the form to load
# except Exception as e:
#     print("Error finding the 'Enter a New Project' link:", e)
#     driver.quit()
#     exit()

# # Step 4: Loop Through CSV and Fill Form
# for index, row in df.iterrows():
#     time.sleep(2)  # Ensure the form is loaded before filling

#     # Fill required form fields, using "NA" for missing values
#     driver.find_element(By.NAME, "primary_builder").send_keys(row.get("Builder Name", "NA"))
#     driver.find_element(By.NAME, "address").send_keys("NA")  # Address missing in CSV
#     driver.find_element(By.NAME, "location").send_keys(f"{row.get('District', 'NA')}, {row.get('State', 'NA')}, {row.get('Tehsil', 'NA')}")
#     driver.find_element(By.NAME, "property_types").send_keys(row.get("Project Category", "NA"))
#     driver.find_element(By.NAME, "completion_date").send_keys(row.get("Declared Date Of Completion", "NA"))
#     driver.find_element(By.NAME, "description").send_keys("NA")  # Description missing
#     driver.find_element(By.NAME, "rera_registration_date").send_keys(row.get("Project Registration Date", "NA"))
#     driver.find_element(By.NAME, "reason_for_creation").send_keys("NA")  # Reason for Creation missing
#     driver.find_element(By.NAME, "sales_person_name").send_keys("NA")  # Salesperson Name missing
#     driver.find_element(By.NAME, "sales_person_email").send_keys("NA")  # Salesperson Email missing

#     print(f"Filled form for record {index + 1}")

#     # Do NOT submit the form
#     time.sleep(2)  # Pause before next entry

# # Close the browser after all records are processed
# driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from datetime import datetime
import pandas as pd
import time

# Configuration (Update these values)
CSV_FILE = "up_project_details.csv"  # Replace with your actual CSV file
LOGIN_URL = "https://xidbackend.99acres.com/index.php/mainpage/login"  # Replace with your login page URL
USERNAME = "backend.ops"  # Replace with your actual username
PASSWORD = "123456"  # Replace with your actual password
NEW_PROJECT_XPATH = "/html/body/table[2]/tbody/tr[3]/td[1]/table/tbody/tr[5]/td/a"  # Update based on actual hyperlink text

# Load CSV Data
df = pd.read_csv(CSV_FILE)  # Use tab delimiter since data looks tab-separated

# Setup Selenium WebDriver (Ignore SSL errors)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--ignore-certificate-errors")  # Bypass SSL warning
driver = webdriver.Chrome(options=chrome_options)

# Step 1: Open Login Page
driver.get(LOGIN_URL)
time.sleep(2)

# Step 2: Handle SSL Warning (Click 'Advanced' and proceed)
try:
    advanced_button = driver.find_element(By.ID, "details-button")
    advanced_button.click()
    time.sleep(1)
    proceed_link = driver.find_element(By.ID, "proceed-link")
    proceed_link.click()
    time.sleep(2)
except Exception:
    print("No SSL warning found. Proceeding to login...")

# Step 3: Enter Username & Password
driver.find_element(By.NAME, "username").send_keys(USERNAME)  # Update field names if needed
driver.find_element(By.NAME, "password").send_keys(PASSWORD)
driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)  # Press Enter to log in
time.sleep(3)  # Wait for page load

# Step 4: Click "Enter a New Project"
try:
    new_project_link = driver.find_element(By.XPATH, NEW_PROJECT_XPATH)
    new_project_link.click()
    time.sleep(2)
except Exception as e:
    print("Error finding the 'Enter a New Project' link:", e)
    driver.quit()
    exit()

# Step 5: Loop Through Each Row in CSV and Fill the Form
for index, row in df.iterrows():
    time.sleep(2)  # Ensure form is loaded
    print("row is", row)

    driver.refresh()

    # ---- Fill Required Form Fields ----
    driver.find_element(By.ID, "formBuilderId").send_keys(row.get("Registration Number", "NA").replace("\n", ", "))  # Handle multi-line names
    driver.find_element(By.ID, "address").send_keys("NA")  # Address not in CSV

    # ---- Select City from Dropdown ----
    city_dropdown = Select(driver.find_element(By.ID, "city_id"))
    city_value = row.get("District", "NA")
    city_dropdown.select_by_visible_text(city_value)

    # ---- Select Locality from Dropdown ----
    # locality_dropdown = Select(driver.find_element(By.ID, "locality_id"))
    # locality_value = row.get("Tehsil", "NA")
    # locality_dropdown.select_by_visible_text(locality_value)

    # ---- Select Society from Dropdown ----
    # society_dropdown = Select(driver.find_element(By.ID, "building_id"))
    # society_value = row.get("Project Name", "NA")
    # society_dropdown.select_by_visible_text(society_value)

    #driver.find_element(By.NAME, "Property Types").send_keys(row.get("Project Category", "NA")) ===> not available
    #possession status ===> not available
    driver.find_element(By.ID, "completionDate").send_keys(row.get("Declared Date Of Completion", "NA"))
    # driver.find_element(By.NAME, "launch_date").send_keys("NA")  # Launch Date missing
    driver.find_element(By.ID, "description").send_keys(row.get("Project Category", "NA"))  # Description missing
    driver.find_element(By.ID, "reraRegistrationNumber").send_keys(row.get("Registration Number", "NA"))

    # rera_date = row.get("Project Registration Date", "NA")
    # if rera_date == "NA" or not rera_date.strip():  # If missing or empty
    #     checkbox = driver.find_element(By.NAME, "reraDateAvailable")  # Checkbox ID (change if needed)
    #     if not checkbox.is_selected():
    #         checkbox.click()
    # else:
    #     driver.find_element(By.NAME, "rera_reg_date").send_keys(rera_date)
    rera_date = row.get("Project Registration Date", "NA")

    if rera_date != "NA" and rera_date.strip():  # Ensure it's not empty
        # Convert date to YYYY-MM-DD format if needed
        formatted_date = datetime.strptime(rera_date, "%d-%m-%Y").strftime("%Y-%m-%d")
        driver.find_element(By.ID, "rera_reg_date").send_keys(formatted_date)
    else:
        # Tick "Not Available" checkbox if date is missing or "NA"
        driver.find_element(By.ID, "reraDateAvailable").click()

    driver.find_element(By.ID, "creationObjective").send_keys("NA")  # Creation Objective Name missing
    # driver.find_element(By.ID, "salesPersonName").send_keys("NA")  # Salesperson Name missing ===> disabled
    # driver.find_element(By.ID, "salesPersonEmail").send_keys("NA")  # Salesperson Email missing ===> disabled

    print(f"Filled form for Project {index + 1}")

    # Do NOT submit the form
    time.sleep(5)  # Pause before next entry


# Step 6: Close the browser
driver.quit()

# 6-7 records