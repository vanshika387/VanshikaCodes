from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re, os, time, datetime, shutil
from selenium.webdriver.support.select import Select
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
from openpyxl.workbook import Workbook
from selenium.common.exceptions import NoSuchElementException
import csv
import pdb
from io import BytesIO
from datetime import date
import json
#chrome_options = webdriver.ChromeOptions() 
def fetch_table_data(driver, table_id):
    """
    Fetch the entire table data once and store it in a list.
    
    :param driver: Selenium WebDriver
    :param table_id: The ID of the table to extract data from
    :return: List of rows (each row is a list of cell values)
    """
    # Locate the table
    table = driver.find_element(By.ID, table_id)

    # Get all rows of the table
    rows = table.find_elements(By.TAG_NAME, 'tr')

    table_data = []
    
    # Loop through rows (skip header row)
    for row in rows[1:]:  # Skip header row
        
        cells = row.find_elements(By.TAG_NAME, 'td')
        row_data = [cell.text for cell in cells]
        table_data.append(row_data)
    
    return table_data



Attempted_date_var = str(date.today())
maindirectory = os.path.abspath(os.getcwd())
HTML = os.path.join(maindirectory, 'OC')
if not os.path.isdir(HTML):
    os.makedirs(HTML)
HTML_PAGE_make_dir = os.path.join(HTML, str(Attempted_date_var))
 
            
if not os.path.isdir(HTML_PAGE_make_dir):
    os.makedirs(HTML_PAGE_make_dir)
chrome_options = webdriver.ChromeOptions()     
settings = {"recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}],
            "selectedDestinationId": "Save as PDF", "version": 2,"isCssBackgroundEnabled": True,"margins":0  }
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
         "savefile.default_directory": HTML_PAGE_make_dir}
chrome_options.add_experimental_option('prefs', prefs)

chrome_options.add_argument('--enable-print-browser')
chrome_options.add_argument('--kiosk-printing') 

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.up-rera.in/projects")
driver.maximize_window()
cnt = 0
cc="NO"
table_data = fetch_table_data(driver, 'grdPojDetail') 
print(table_data)
matching_rows = []
with open("up-focus.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
    for row_1 in records:
        time.sleep(5)
        xid = row_1[0]
        reg_id = xid
        match_found = False
        data = {}
         

        for index, row in enumerate(table_data, start=1):  # Start index from 1
            formatted_index = f"{index:02}"  
            if len(row) >= 4 and row[3] == reg_id:  # Check if the 4th cell matches the registration ID
                row_text = row[0]
                
                matching_rows.append((reg_id, formatted_index, row_text))  # Append row info to matching_rows
                match_found = True
                x = formatted_index
                match_found = True  # Set the flag to True when a match is found
                print(f"Match found for {reg_id} in row {formatted_index}: {row_text}")  # Print the match immediately
            
                try:
                    print(driver.find_element(By.XPATH, '//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[3]').text)
                    #print(x)
                    try:
                        data['Registration Number'] = driver.find_element(By.XPATH, '//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[4]').text
                        data['Builder Name'] = driver.find_element(By.XPATH, '//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[2]').text
                        data['Project Category'] = driver.find_element(By.XPATH, '//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[5]').text
                    except:
                        continue
                    data['Project Name'] =driver.find_element(By.XPATH,'//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[3]' ).text
                    data['State'] = 'Uttar Pradesh'
                    data['District'] =driver.find_element(By.XPATH,'//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[6]').text 
                    time.sleep(2)
                    try:
                        driver.find_element(By.XPATH, '//*[@id="grdPojDetail"]/tbody/tr['+str(x)+']/td[9]/a').click()
                    except:
                        continue
                    #print('pass')
                    window_after = driver.window_handles[1]
                    driver.switch_to.window(window_after)
                    data['Project Registration Date'] = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_prjregdate').text
                    data['Declared Date Of Completion'] = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_Lblproposedenddt').text
                    
                    data['Tehsil'] =driver.find_element(By.ID,'ctl00_ContentPlaceHolder1_lbltechsil' ).text
                    
                    link = driver.find_element(By.XPATH, '//a[@href="viewprojects"]')

                    # Ensure the link is clickable (optional but good practice)
                    ActionChains(driver).move_to_element(link).click().perform()
                    
                    #driver.find_element(By.XPATH, '//*[@data-target="#exampleModal"]').click()
                    #driver.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_dv_oc"]/div[2]/a').click()
                    #/html/body/form/div[3]/section[2]/div/div/div/div/div[2]/div[3]/div/div/div/div/div/div[2]/div[2]/a
                    time.sleep(3)
                    
                    driver.switch_to.window(driver.window_handles[2])
                    time.sleep(1)
                    data['Total area in round figure (Sq.mt.)']  = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_lblTotalArea').get_attribute('value')
                    data['Latitude']  = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_lblLat1').get_attribute('value')
                    data['Longtitude']  = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_lblLong1').get_attribute('value')
                    data['Architect Name']  = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_lblArchName').get_attribute('value')
                    registration_number = data['Registration Number']

                    # Locate the table
                    table = driver.find_element(By.ID, 'ShowTableApartment')

                    # Extract table headers
                    headers = [header.text for header in table.find_elements(By.TAG_NAME, 'th')]

                    print("Length of Headers:", len(headers))

                    if len(headers) == 12:
                        csv_file1 = 'apartment_data3.csv'
                    else:
                        csv_file1 = 'others_data3.csv'

                    # Add "Registration Number" as the first header
                    headers.insert(0, "Registration Number")

                    # Extract table rows
                    rows = table.find_elements(By.TAG_NAME, 'tr')

                    # Prepare the data
                    data_1 = []
                    for row in rows[1:]:  # Skip the header row
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        row_data = [registration_number] + [cell.text for cell in cells]
                        data_1.append(row_data)

                    # Determine the CSV file based on the number of columns
                    # if len(headers) == 12:
                    #     csv_file1 = 'apartment_data2.csv'
                    # else:
                    #     csv_file1 = 'others_data2.csv'

                    # Save data to CSV
                    file_exists1 = os.path.isfile(csv_file1)
                    with open(csv_file1, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        if not file_exists1:  # Write header only if the file doesn't exist
                            writer.writerow(headers)
                        writer.writerows(data_1)  # Write rows

                    print(f"Data saved to {csv_file1}")

                    df = pd.DataFrame([data])
                    print(data)
                # Save to a CSV file
                    csv_file = "up_project_details.csv"
                    file_exists = os.path.isfile(csv_file)

                    try:
                        df.to_csv(csv_file, mode='a', header=not file_exists, index=False)
                        print(f"Data has been saved to {csv_file}.")
                    except Exception as file_error:
                        print(f"Error saving CSV: {file_error}")
                    
                    driver.close()
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[1])
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    
                    #store data
                    
                    continue
                except:
                    driver.close()
                    window_after = driver.window_handles[0]
                    driver.switch_to.window(window_after)
                    print('break')
                    continue
            
        time.sleep(3)









