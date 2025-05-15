from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import os, csv, time
from selenium.webdriver.common.keys import Keys
import requests

# Define the URL
url = "https://haryanarera.gov.in/admincontrol/registered_projects/2"

# Initialize the WebDriver
driver = webdriver.Chrome()

# Define the download folder for documents
download_folder = "oc"
os.makedirs(download_folder, exist_ok=True)

# Output CSV file
csv_file = "Haryana_project_details.csv"

# Initialize the CSV with headers
headers = [
    "Registration Certificate Number",
    "Project Name",
    "Builder",
    "Project Location",
    "Project District"
]
facility_names = [
    "INTERNAL ROADS AND PAVEMENTS",
    "WATER SUPPLY SYSTEM",
    "STORM WATER DRAINAGE",
    "ELECTRICITY SUPPLY SYSTEM",
    "SEWAGE TREATMENT & GARBAGE DISPOSAL",
    "STREET LIGHTING",
    "SECURITY AND FIRE FIGHTING",
    "PLAYGROUNDS AND PARKS",
    "CLUB HOUSE/COMMUNITY CENTRE",
    "SHOPPING AREA",
    "RENEWABLE ENERGY SYSTEM",
    "SCHOOL",
    "HOSPITAL/DISPENSARY",
    "ANY OTHER"]
financial_information = [
    "No. of Flats/Apartments constructed",
    "No. of Flats/ Apartments booked"
]
fields_to_extract = [
    "Land area of the project",
    "Projected date of completion",
    "Percentage completion",
    "FLOORING DETAILS OF VARIOUS PARTS OF HOUSE",
    "KITCHEN DETAILS",
    "DOORS AND WINDOS FRAMES",
    "ELECTRIC FITTINGS",
    "LIFT DETAILS",
    "ELECTRICAL FITTINGS",
    "INTERNAL FINISHING"
]
documents = [ "Document URL",
    "OC Document Path"]

if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
    pd.DataFrame(columns=headers + facility_names + financial_information + fields_to_extract + documents).to_csv(csv_file, index=False)

try:
    # Open the webpage
    driver.get(url)

    with open("haryana-focus.csv", "r") as csvfile:
        records = csv.reader(csvfile, delimiter=",")
        next(records)  # Skip the header row

        for row in records:
            xid = row[0]
            print(f"Processing ID: {xid}")

            # Search for the project
            search_input = driver.find_element(By.XPATH, '//*[@id="compliant_hearing_filter"]/label/input')
            search_input.send_keys(Keys.CONTROL, 'a')
            search_input.send_keys(xid)
            try:
            # Extract project data
                data = {
                    "Registration Certificate Number": driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[2]').text,
                    "Project Name": driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[4]').text,
                    "Builder": driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[5]').text,
                    "Project Location": driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[6]').text,
                    "Project District": driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[7]').text
                }

                # # Download document
                # try:
                #     document_link_element = driver.find_element(By.XPATH, "//a[contains(@href, 'view_corrigendum')]")
                #     document_url = document_link_element.get_attribute("href")
                #     data["Document URL"] = document_url

                #     response = requests.get(document_url)
                #     if response.status_code == 200:
                #         document_path = os.path.join(download_folder, f"{xid.replace('/', '-')}-OC_uploaded.pdf")
                #         with open(document_path, "wb") as file:
                #             file.write(response.content)
                #         data["OC Document Path"] = document_path
                #     else:
                #         data["OC Document Path"] = "Download Failed"
                # except Exception as e:
                #     print(f"Error downloading document for {xid}: {e}")
                #     data["Document URL"] = "Not Found"
                #     data["OC Document Path"] = "Not Available"

            
                driver.find_element(By.XPATH, '//*[@id="compliant_hearing"]/tbody/tr/td[9]/a').click()
            except Exception as e:
                print(f"Error opening project details for {xid}: {e}")
                continue
            
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(5)
            # Extract facilities
            for facility in facility_names:
                try:
                    row = driver.find_element(By.XPATH, f"//tr[td[contains(text(), '{facility}')]]")
                    next_column = row.find_element(By.XPATH, "./td[3]").text  # Extract from the second column
                    data[facility] = next_column.strip()
                except Exception as e:
                    data[facility] = "Not Found"
                    print(f"Could not find {facility}: {e}")  # Debugging output
            
            # Extract financial information
            for field in financial_information:
                try:
                    row = driver.find_element(By.XPATH, f"//tr[td[contains(text(), '{field}')]]")
                    next_column = row.find_element(By.XPATH, "./td[2]").text  # Extract from the second column
                    data[field] = next_column.strip()
                except Exception as e:
                    data[field] = "Not Found"
                    print(f"Could not find {field}: {e}")  # Debugging output

            # Extract additional fields
            for field in fields_to_extract:
                try:
                    if field == "Land area of the project":
                        field_row = driver.find_element(By.XPATH, "//td[label[contains(text(), 'Land area of the project')]]/following-sibling::td[2]/b")
                    elif field == "Projected date of completion":
                        field_row = driver.find_element(By.XPATH, "//td[label[contains(text(), 'Projected date of completion')]]/following-sibling::td[1]/b")
                    elif field == "Percentage completion":
                        field_row = driver.find_element(By.XPATH, "//td[label[contains(text(), 'Percentage completion')]]/following-sibling::td[1]/b")
                    else:
                        field_row = driver.find_element(By.XPATH, f"//td[contains(text(), '{field}')]/following-sibling::td[1]/b")
                    data[field] = field_row.text.strip()
                except:
                    data[field] = "Not available"

            # Download document
            try:
                document_link_element = driver.find_element(By.XPATH, "//a[contains(@href, 'view_corrigendum')]")
                document_url = document_link_element.get_attribute("href")
                data["Document URL"] = document_url

                response = requests.get(document_url)
                if response.status_code == 200:
                    document_path = os.path.join(download_folder, f"{xid.replace('/', '-')}-OC_uploaded.pdf")
                    with open(document_path, "wb") as file:
                        file.write(response.content)
                    data["OC Document Path"] = document_path
                else:
                    data["OC Document Path"] = "Download Failed"
            except Exception as e:
                print(f"Error downloading document for {xid}: {e}")
                data["Document URL"] = "Not Found"
                data["OC Document Path"] = "Not Available"

            # Append data to CSV
            try:
                pd.DataFrame([data]).to_csv(csv_file, mode="a", header=False, index=False)
                print(f"Data saved for {xid}")
            except Exception as e:
                print(f"Error saving data for {xid}: {e}")

            # Close project details tab and return to main
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()
    print("Processing complete.")
