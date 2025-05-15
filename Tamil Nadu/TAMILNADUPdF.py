import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import glob
import re

# Function to clean file names
def clean_filename(filename):
    return re.sub(r'[\/:*?"<>|]', '_', filename)  # Replace invalid characters with '_'

options = Options()
options.headless = True
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
driver.get("https://rera.tn.gov.in/registered-building/tn")
driver.maximize_window()
wait = WebDriverWait(driver, 10)
current_directory = os.getcwd()
mypdf_directory = os.path.join(current_directory, "mypdf")

def getText(xpath):
    try:
        v = driver.find_element(By.XPATH, xpath).text
        return v
    except:
        return ''

def download_FP_with_ctrl_s(url, textName, reg_no):
    # Define the base directory for storing PDFs
    target_folder = os.path.abspath("Stage of Construction and Site Photographs with date")
    target_file = f"{clean_filename(textName)} {clean_filename(reg_no)}.pdf"
    
    # Ensure the target folder exists
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Create a temporary download folder
    download_folder = os.path.abspath("temp_downloads")
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    # Set up Chrome options
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_folder,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Set up the Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open the URL
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    
    # Simulate Ctrl + S
    ActionChains(driver).key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
    time.sleep(10)  # Wait for the download to complete
    
    # Close the browser
    driver.quit()
    
    # Find the most recently downloaded file
    list_of_files = glob.glob(os.path.join(download_folder, '*'))
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        
        # Move and rename the file
        new_path = os.path.join(target_folder, target_file)
        os.rename(latest_file, new_path)
        print(f"PDF downloaded and saved as {new_path}")
    else:
        print("No files were downloaded.")
    
    # Clean up the temporary download folder
    if os.path.exists(download_folder):
        os.rmdir(download_folder)

with open("2025_building_data.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
    for row in records:
        time.sleep(2)
        xid = row[0]
        print(xid)
        project_details = {}
         

        time.sleep(2)
        input_element = driver.find_element(By.XPATH, '//*[@id="example1_filter"]/label/input')

        # Clear the input field first, just in case
        input_element.clear()

        # Send Ctrl + A (select all text) and then send new text if needed
        input_element.send_keys(Keys.CONTROL, 'a')
        input_element.send_keys(xid)
         

        fileName = xid.replace(r'/', '-')

        
        time.sleep(1)
        reg_no = xid
        
        prom_address = getText('//*[@id="example1"]/tbody/tr/td[3]')
        
        Project_detail_address = getText('//*[@id="example1"]/tbody/tr/td[3]')
         
        proj_completion_date = getText('//*[@id="example1"]/tbody/tr/td[6]')

        other_details_Lat_long = getText('//*[@id="example1"]/tbody/tr/td[7]/span')

        project_details['reg_no'] = reg_no
        project_details['prom_address'] = prom_address
        project_details['Project_detail_address'] = Project_detail_address
        project_details['proj_completion_date'] = proj_completion_date
        project_details['other_details_Lat_long'] = other_details_Lat_long
        
        cuurent_status = getText('//*[@id="example1"]/tbody/tr/td[8]')
        try:
            driver.find_element(By.XPATH, '//*[@id="example1"]/tbody/tr/td[7]/a[2]').click()
        except:
            continue
        time.sleep(3)

        #Switching to project details page 
        driver.switch_to.window(driver.window_handles[1])

         # Extract text
        try:
            text_element = driver.find_element(By.XPATH, '//*[@id="Documents"]/div/div[3]/div[2]/div/div[1]/p1')
            text_value = text_element.text.strip()
            print(f"Extracted text: {text_value}")
        except Exception as e:
            print(f"Error extracting text")
            text_value = "unknown"

        # Extract PDF link
        try:
            link_element = driver.find_element(By.XPATH, '//*[@id="Documents"]/div/div[3]/div[2]/div/div[2]/p/a')
            pdf_url = link_element.get_attribute("href")
            print(f"Extracted PDF URL: {pdf_url}")
        except Exception as e:
            print(f"Error extracting PDF link")
        
        download_FP_with_ctrl_s(pdf_url, text_value, reg_no)

        #Closing the project details page
        driver.close()

        driver.switch_to.window(driver.window_handles[0])
         
        # try:
        #     # Prepare data to be written to CSV
        #     csv_file = 'tamilnadu_project_details.csv'

        #     # # Write data to CSV, appending if the file already exists
        #     # with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        #     #     writer = csv.DictWriter(file, fieldnames=project_details.keys())
                
        #     #     # Write header if the file is empty
        #     #     if file.tell() == 0:
        #     #         writer.writeheader()
                
        #     #     # Write the project details row
        #     #     writer.writerow(project_details) 
        # except:
        #     pass
            #driver.find_element(By.XPATH, '/html/body/div[1]/div/div[6]/button[1]').click()
        
         

        print("HERE1")









