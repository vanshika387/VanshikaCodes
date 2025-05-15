import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Constants
INPUT_CSV = "focus.csv"  # Input CSV file
OUTPUT_CSV = "output.csv"  # Output CSV file
APARTMENT_CSV = "apartment.csv"  # Apartment CSV file
PROFESSIONAL_CSV = "professional.csv"  # Professional CSV file
PROMOTER_PAST_DETAILS_CSV = "promoter_past_details.csv"  # Promoter past details CSV file
URL = "https://reraonline.kerala.gov.in/SearchList/Search"

# Check if output file is empty (or doesn't exist)
# Check if output files are empty (or don't exist)
file_exists_main = os.path.exists(OUTPUT_CSV) and os.path.getsize(OUTPUT_CSV) > 0
file_exists_apartment = os.path.exists(APARTMENT_CSV) and os.path.getsize(APARTMENT_CSV) > 0
file_exists_proffessional = os.path.exists(PROFESSIONAL_CSV) and os.path.getsize(PROFESSIONAL_CSV) > 0
file_exists_promoter_past_details = os.path.exists(PROMOTER_PAST_DETAILS_CSV) and os.path.getsize(PROMOTER_PAST_DETAILS_CSV) > 0

# Set up Selenium WebDriver
driver = webdriver.Chrome()

# Open the website
driver.get(URL)
time.sleep(2)  # Wait for page to load

try:
    # Open input CSV for reading and output CSV for appending
    with open(INPUT_CSV, newline='', encoding="utf-8") as infile, \
         open(OUTPUT_CSV, 'a', newline='', encoding="utf-8") as outfile_main, \
         open(APARTMENT_CSV, 'a', newline='', encoding="utf-8") as outfile_apartment, \
         open(PROFESSIONAL_CSV, 'a', newline='', encoding="utf-8") as outfile_proffessional, \
         open(PROMOTER_PAST_DETAILS_CSV, 'a', newline='', encoding="utf-8") as outfile_promoter_past_details:

        reader = csv.reader(infile)
        writer_main = csv.writer(outfile_main)
        writer_apartment = csv.writer(outfile_apartment)
        writer_proffessional = csv.writer(outfile_proffessional)
        writer_promoter_past_details = csv.writer(outfile_promoter_past_details)

        # Write header only if file is empty
        if not file_exists_main:
            writer_main.writerow(["Registration Number", "Total Land Area", "Project Type", "Total Units", "Locality", "Proposed Area to be Constructed", "Building Name"])

        next(reader)  # Skip header of input file

        for row in reader:  # Read from the second line onwards
            reg_number = row[0]  # Modify index based on CSV structure

            print(f"Processing registration number: {reg_number}")
            
            time.sleep(1)

            # Find input field and enter value
            driver.find_element(By.ID, "CertiNo").clear()
            driver.find_element(By.ID, "CertiNo").send_keys(reg_number)
            driver.find_element(By.ID, "CertiNo").send_keys(Keys.RETURN)

            driver.find_element(By.ID, "btnSearch").click()
            time.sleep(3)  # Wait for results to load
            
            # Click the "View" button using the correct XPath
            driver.find_element(By.XPATH, "//*[@id='gridview']/div[1]/div/table/tbody/tr/td[5]/b/a").click()
            time.sleep(3)  # Wait for new tab
            
            # Switch to the new tab
            driver.switch_to.window(driver.window_handles[1])

            #Switch to project details tab
            driver.find_element(By.XPATH, '//*[@id="Divpan"]/div/div/ul/li[1]/a').click()

            # Extract data
            total_land_area = driver.find_element(By.XPATH, "//*[@id='DivGeneral']/div/div/div[2]/div[3]/div[4]/div/label/span").text
            
            # Remove extra text and extract only the needed parts
            project_type = driver.find_element(By.XPATH, '//*[@id="DivGeneral"]/div/div/div[2]/div[1]/div[5]/div').text
            project_type = project_type.replace("Project Type :", "").strip()

            total_units = driver.find_element(By.XPATH, '//*[@id="DivProject"]/div/div/div[2]/div[1]/div[2]/div[2]/div[6]').text
            total_units = total_units.replace("Number of Residential Units (As per Sanctioned Plan) ", "").strip()

            locality = driver.find_element(By.XPATH, '//*[@id="DivProject"]/div/div/div[2]/div[1]/div[4]/div[2]/div[8]').text
            locality = locality.replace("Locality", "").strip()

            #Switch to Promoter's details tab
            driver.find_element(By.XPATH, '//*[@id="Divpan"]/div/div/ul/li[2]/a').click()
            time.sleep(3)

            proposed_area_to_be_constructed = driver.find_element(By.XPATH, '//*[@id="DivTrackRecord"]/div/div/div[2]/div[1]/div/div/div[6]').text
            proposed_area_to_be_constructed = proposed_area_to_be_constructed.replace("proposed Area to be constructed(Sqm) ", "").strip()

            try:
                table = driver.find_element(By.XPATH, '//*[@id="DivPastExpNew"]/div[2]/div/div[2]/div/table')
                if not file_exists_promoter_past_details:
                    headers = ["Registration Number"]
                    header_row = table.find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "th")  # Find header row
                    headers.extend([th.text.strip() for th in header_row])  # Extract header text
                    writer_promoter_past_details.writerow(headers)
                    file_exists_promoter_past_details = True  # Prevent rewriting headers in next iterations

                # Extract table rows
                rows = table.find_elements(By.TAG_NAME, "tr")[1:] 

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    data = [col.text.strip() for col in cols]  # Extract text from each column
                    if data:  # Avoid empty rows
                        writer_promoter_past_details.writerow([reg_number] + data)
            except:
                pass

            # Switch to Construction Progress tab
            driver.find_element(By.XPATH, '//*[@id="Divpan"]/div/div/ul/li[4]/a').click()
            time.sleep(3)
            try:
                building_name = driver.find_element(By.XPATH, '//*[@id="DivBuilding"]/div/div/div[2]/div/table/tbody/tr[2]/td[2]').text
            except:
                building_name = "N/A"

            #Saving the apartment type table
            # Extract apartment table data
            try:
                table = driver.find_element(By.XPATH, "//*[@id='DivBuilding']/div/div/div[2]/div/table/tbody/tr[3]/td[3]/table")
                if not file_exists_apartment:
                    headers = ["Registration Number"]
                    header_row = table.find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "th")  # Find header row
                    headers.extend([th.text.strip() for th in header_row])  # Extract header text
                    writer_apartment.writerow(headers)
                    file_exists_apartment = True  # Prevent rewriting headers in next iterations

                # Extract table rows
                rows = table.find_elements(By.TAG_NAME, "tr")[1:] 

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    data = [col.text.strip() for col in cols]  # Extract text from each column
                    if data:  # Avoid empty rows
                        writer_apartment.writerow([reg_number] + data)
            except:
                pass
            
            #Switch to proffessional information tab
            driver.find_element(By.XPATH, '//*[@id="Divpan"]/div/div/ul/li[5]/a').click()
            time.sleep(3)

            try:
                table = driver.find_element(By.XPATH, '//*[@id="fldindtxt1"]/div[1]/div/div[2]/div/table')
                if not file_exists_proffessional:
                    headers = ["Registration Number"]
                    header_row = table.find_elements(By.TAG_NAME, "tr")[0].find_elements(By.TAG_NAME, "th")  # Find header row
                    headers.extend([th.text.strip() for th in header_row])  # Extract header text
                    writer_proffessional.writerow(headers)
                    file_exists_proffessional = True  # Prevent rewriting headers in next iterations

                # Extract table rows
                rows = table.find_elements(By.TAG_NAME, "tr")[1:] 

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    data = [col.text.strip() for col in cols]  # Extract text from each column
                    if data:  # Avoid empty rows
                        writer_proffessional.writerow([reg_number] + data)
            except:
                pass


            # Write to CSV
            writer_main.writerow([reg_number, total_land_area, project_type, total_units, locality, proposed_area_to_be_constructed, building_name])

            # Close the new tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

finally:
    driver.quit()
