from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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
import csv, requests
import pdb
from io import BytesIO
from datetime import date

#chrome_options = webdriver.ChromeOptions() 

#chrome_options = webdriver.ChromeOptions() 
chrome_options = Options()
'''download_dir = "mypdf"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set the download directory
        "download.prompt_for_download": False,        # Disable download prompt
        "download.directory_upgrade": True,           # Allow directory change
        "safebrowsing.enabled": True                  # Enable safe browsing
    })
'''
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#driver = webdriver.Firefox()
driver.get("https://rera.tn.gov.in/registered-building/tn")
driver.maximize_window()
wait = WebDriverWait(driver, 10)
current_directory = os.getcwd()
mypdf_directory = os.path.join(current_directory, "mypdf")

# If the directory does not exist, create it
if not os.path.exists(mypdf_directory):
    os.makedirs(mypdf_directory)    

def getText(xpath):
    try:
        v = driver.find_element(By.XPATH, xpath).text
        return v
    except:
        return ''
    
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
        driver.switch_to.window(driver.window_handles[1])
        # List of labels you want to fetch


        # labels_to_find = [
        #     "Project Name :",
        #     "Project Details :",
        #     "Type of Building :",
        #     "Usage :",
        #     "Site Extent(Sq.m) :",
        #     "Total No. of Dwelling Units including all Phases/Villas :",
        #     "Stage of Construction :",
        #     "Project Completion Date :",
        #     "Latitude :",
        #     "Longitude :"
        # ]

        # # Find the "Proposed Project Detail" header
        # header = driver.find_element(By.XPATH, "//span[contains(text(), 'Proposed Project Detail')]")

        # # Find all rows under this header section that contain the required labels
        # rows = header.find_elements(By.XPATH, "//following-sibling::div[contains(@class, 'form_sec')]//div[contains(@class, 'form-group')]")

        # # Create an empty dictionary to store the scraped data
        

        # # Loop through each row and extract the label (p1) and its corresponding value (p)
        # for row in rows:
        #     try:
        #         # Extract the label and value
        #         label = row.find_element(By.XPATH, ".//p1").text.strip()
                 
        #         # Check if the label is in the list of labels_to_find
        #         if label in labels_to_find:
        #             # Extract the value corresponding to the label
        #             value = row.find_element(By.XPATH, ".//p").text.strip()
                    
        #             # Add the label and value to the dictionary
        #             project_details[label] = value
        #     except Exception as e:
        #         print(f"Error while extracting data: {str(e)}")

        # # Print the extracted project details
        # #print(project_details)
         
        project_details['site_address'] = getText('//*[@id="village_detail"]/div/div/div/div[2]/p')
        
        labels_to_find1 = [
            "Solid Waste Disposal by:",
            "Solid Waste Disposal (Internal arrangement Document) :",
            "Water Supply Source :",
            "Sewage Disposal by :",
            "Renewable Energy If Applicable(Provision made in terrace floor) :",
            "Fire Fighting & Emergency Evacuation services as per MSB Norms for MSB's (ie., More than stilt + 5 Floors) :",
            "Internal Road :",
            "Others :"
        ]

        # Loop through each label and extract the corresponding value
        header = driver.find_element(By.XPATH, "//span[contains(text(), 'Plan of Development Works')]")

        # Find all rows under this header section that contain the required labels
        rows = header.find_elements(By.XPATH, "//following-sibling::div[contains(@class, 'form_sec')]//div[contains(@class, 'form-group')]")

        # Create an empty dictionary to store the scraped data
        

        # Loop through each row and extract the label (p1) and its corresponding value (p)
        for row in rows:
            try:
                # Extract the label and value
                label = row.find_element(By.XPATH, ".//p1").text.strip()
                 
                # Check if the label is in the list of labels_to_find
                if label in labels_to_find1:
                    # Extract the value corresponding to the label
                    value = row.find_element(By.XPATH, ".//p").text.strip()
                    
                    # Add the label and value to the dictionary
                    project_details[label] = value
            except Exception as e:
                print(f"Error while extracting data: {str(e)}")

        # Print the extracted project details
        #print(project_details)
         
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element(By.XPATH, '//*[@id="example1"]/tbody/tr[1]/td[7]/a[1]').click()
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[1])

        #print(project_details)

         

        text = driver.find_element(By.XPATH, '//*[@id="promoter_det_body"]/div/div[1]').text
        if text == 'Promoter Detail':
            project_details["Project Developed by :"] =   getText('//*[@id="promoter_det_body"]/div/div[2]/div[1]/div/div[2]/p')
            project_details["Type of Promoter :"] =   getText('//*[@id="promoter_det_body"]/div/div[2]/div[2]/div/div[2]/p')
            project_details["Firm Name :"] =   getText('//*[@id="promoter_det_body"]/div/div[2]/div[3]/div/div[2]/p')
        
        # Loop through each label and extract the corresponding value
        

        # Print the extracted promoter details
        print(project_details)

        # Print the extracted project details
         
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
         
        try:
            # Prepare data to be written to CSV
            csv_file = 'tamilnadu_project_details.csv'

            # Write data to CSV, appending if the file already exists
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=project_details.keys())
                
                # Write header if the file is empty
                if file.tell() == 0:
                    writer.writeheader()
                
                # Write the project details row
                writer.writerow(project_details)
                        
         
                
            
        except:
            pass
            #driver.find_element(By.XPATH, '/html/body/div[1]/div/div[6]/button[1]').click()
        
         
        
        print("HERE1")
         
         
          
              
                   

 
         

