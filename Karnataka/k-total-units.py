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
import csv,os,requests
import pdb
from io import BytesIO
from datetime import date
from bs4 import BeautifulSoup

from pathlib import Path
from selenium.webdriver.chrome.options import Options
#chrome_options = webdriver.ChromeOptions() 

default_download_dir = str(Path.home() / "Downloads")  # Default downloads folder
destination_dir = "downloaded_pdfs"
if not os.path.exists(destination_dir):
    os.makedirs(destination_dir)

driver = webdriver.Chrome()
#driver.get("https://rera.karnataka.gov.in/projectViewDetails")
driver.get("https://rera.karnataka.gov.in/home?language=en")
time.sleep(5)
driver.maximize_window()
driver.find_element(By.XPATH, '//*[@id="main_nav"]/ul[2]/li[5]/a').click()
time.sleep(5)
driver.find_element(By.XPATH, '//*[@id="main_nav"]/ul[2]/li[5]/ul/li[1]/a').click()
#driver.maximize_window()
ids_group = []
cnt = 0
cc="NO"
wait = WebDriverWait(driver, 10)
c=0
# Function to download files
target_texts= [
                    "Area Development Plan of Project Area",
                    "Brochure of Current Project",
                    "Project Specification",
                ]
 


   
 

with open("focus.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
    for row in records:
        time.sleep(2)
        xid = row[0]
        
        print(xid)
        driver.find_element(By.ID, 'regNo2').send_keys(Keys.CONTROL, 'a')
        driver.find_element(By.ID, 'regNo2').send_keys(xid)
        driver.find_element(By.NAME, 'btn1').click()
        time.sleep(4)
        #folder = 'RAA00360-EX1-071218' /html/body/section[2]/div[2]/div/div/div/div[1]/div/div/div[2]/div[2]/table/tbody/tr/td[4]/b/a
        fileName = xid.replace(r'/', '-')
        time.sleep(3)
        proj_name = driver.find_element(By.XPATH, '//*[@id="approvedTable"]/tbody/tr/td[6]').text
        prom_name = driver.find_element(By.XPATH, '//*[@id="approvedTable"]/tbody/tr/td[5]').text
        proj_status = driver.find_element(By.XPATH, '//*[@id="approvedTable"]/tbody/tr/td[7]').text
        proj_district = driver.find_element(By.XPATH, '//*[@id="approvedTable"]/tbody/tr/td[8]').text
        try:
            driver.find_element(By.XPATH, '//*[@id="approvedTable"]/tbody/tr/td[4]/b/a').click()
            time.sleep(1)
        except:
            continue
        time.sleep(3)
        try:
            driver.find_element(By.XPATH, "//a[contains(text(), 'Promoter Details')]").click()
        except:
            pass
        try:
            promtor_type_element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class, "row") and contains(., "Promoter Type")]/div[2]/p')
                )
            )
            promoter_type = promtor_type_element.text.strip()
        except:
            try:
                promtor_type_element = driver.find_element(By.XPATH, '//div[contains(@class, "row") and (contains(., "Type of Firm") or contains(.,"Firm Type"))]/div[2]/p')
                    
                promoter_type = promtor_type_element.text.strip()
            except:
                pass
        # time.sleep(5)
        project_details_tab = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Project Details')]"))
        )
        project_details_tab.click()
        time.sleep(1)
        # Locate and extract Project Type
        project_type_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "row") and contains(., "Project Type")]/div[2]/p')
            )
        )
        project_type = project_type_element.text.strip()

        # Locate and extract Project Status
        project_status_element = driver.find_element(
            By.XPATH, '//div[contains(@class, "row") and contains(., "Project Status")]/div[4]/p'
        )
        project_status = project_status_element.text.strip()

        # Locate and extract Project Status
        try:
            project_propCOmp_element = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "Proposed Project Completion Date")]/div[4]/p'
            )
        except:
            project_propCOmp_element = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "Proposed Completion Date")]/div[4]/p'
            )
        project_comp_date = project_propCOmp_element.text.strip()

        project_address_element = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[contains(@class, "row") and contains(., "Project Address")]/div[2]/p')
            )
        )
        project_address = project_address_element.text.strip()
          # Extract Type of Inventory
        try:
            inventory_type = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[contains(@class, "row") and contains(., "Type of Inventory")]/div[2]/p')
                )
            ).text.strip()
        except:
            inventory_type = ""
        # Extract No of Inventory
        try:
            no_of_inventory = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "No of Inventory")]/div[4]/p'
            ).text.strip()
        except:
            no_of_inventory = ""
        # Extract Carpet Area (Sq Mtr)
        try:
            carpet_area = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "Carpet Area (Sq Mtr)")]/div[2]/p'
            ).text.strip()
        except:
            carpet_area = ""

        try:
            # Extract Area of exclusive balcony/verandah
            balcony_area = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "Area of exclusive balcony/verandah")]/div[4]/p'
            ).text.strip()
        except:
            balcony_area = ''
        # Extract Area of exclusive open terrace if any
        try:
            terrace_area = driver.find_element(
                By.XPATH, '//div[contains(@class, "row") and contains(., "Area of exclusive open terrace if any")]/div[2]/p'
            ).text.strip()
        except:
            terrace_area = ""
        try:
            section_title = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//h1[contains(text(), "Project Architects")]')
                )
            )
            
            # Find the Name element in the same section
            arch_name = section_title.find_element(
                By.XPATH, '../../following-sibling::div//div[contains(@class, "row") and contains(., "Name")]/div[2]/p'
            ).text.strip()
        except:
            arch_name = ""
        try:    
            num_projects_completed = driver.find_element(
                By.XPATH, '../../following-sibling::div//div[contains(@class, "row") and contains(., "Number of Project Completed")]/div[4]/p'
            ).text.strip()
        except:
            num_projects_completed = "" 
         
        '''try:
            driver.find_element(By.XPATH, "//a[contains(text(), 'Uploaded Documents')]").click()
            #driver.find_element(By.XPATH, '//*[@id="site-content"]/div[2]/div/div/div[2]/ul/li[3]/a').click()
            try:
    # Wait for the page to load
                for target_text in target_texts:
                    try:
                        # Wait until the page's body is fully loaded
                        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

                        # Locate the element containing the target text
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{target_text}')]")
                        
                        if elements:
                            print(f"Text '{target_text}' found!")

                            # Find the next link and simulate a click
                            next_link = elements[0].find_element(By.XPATH, ".//following::a[1]")
                            print(f"Clicking link for '{target_text}'...")
                            
                            # Open the link in a new tab
                            ActionChains(driver).key_down(Keys.CONTROL).click(next_link).key_up(Keys.CONTROL).perform()
                            
                            # Wait for the new tab to load
                            time.sleep(3)  # Adjust as necessary
                            
                            # Switch to the new tab
                            driver.switch_to.window(driver.window_handles[-1])
                            
                            # Wait for the new page to load
                            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

                            # Wait for the download to start
                            time.sleep(5)
                            
                            # Check if a file has been downloaded
                            files = [os.path.join(default_download_dir, f) for f in os.listdir(default_download_dir)]
                            files = [f for f in files if os.path.isfile(f)]  # Filter only files
                            if not files:
                                raise FileNotFoundError("No file was downloaded.")
                            
                            latest_file = max(files, key=os.path.getmtime)  # Get the most recently modified file
                            
                            # Extract the original file name and extension
                            original_file_name = os.path.basename(latest_file)
                            file_name, file_extension = os.path.splitext(original_file_name)
                            
                            # Create the new file name with `xid`
                            new_file_name = f"{file_name}_{xid}{file_extension}"
                            
                            # Move and rename the file to the destination directory
                            destination_path = os.path.join(destination_dir, new_file_name)
                            shutil.move(latest_file, destination_path)
                            print(f"Moved {original_file_name} to {destination_dir} as {new_file_name}")
                            
                            # Close the new tab
                            driver.close()
                            
                            # Switch back to the original tab
                            driver.switch_to.window(driver.window_handles[0])
                        else:
                            print(f"Text '{target_text}' not found on the page.")

                    except Exception as e:
                        print(f"An error occurred while processing '{target_text}':", e)

            except Exception as e:
                print("An error occurred:", e)
        except:
            pass
        time.sleep(5)'''
         
        try:
    # Load the web page
            total_flats_value = ""
            occupancy_date_value = ""

            # Locate the tab with href="#completion"
            tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Completion Details')]")
            
            # Check if the tab exists and is visible
            if tab.is_displayed():
                # Click the tab
                tab.click()
                print("Tab clicked successfully!")
                try:
                    total_flats_label = driver.find_element(By.XPATH, "//p[contains(text(), 'Total number of Flats/Apartments of the Project')]")
                    total_flats_value = total_flats_label.find_element(By.XPATH, "following::p[1]").text
                except Exception as e:
                    total_flats_value = "Not found"

                # Locate and extract "Occupancy certificate received date"
                try:
                    occupancy_date_label = driver.find_element(By.XPATH, "//p[contains(text(), 'Occupancy certificate received date')]")
                    occupancy_date_value = occupancy_date_label.find_element(By.XPATH, "following::p[1]").text
                except Exception as e:
                    occupancy_date_value = "Not found"
            else:
                print("Tab exists but is not visible.")
        except NoSuchElementException:
            print("The tab with href='#completion' does not exist on this page.")
        try:
            
            # File name
            csv_file = "karnataka_project_details_final2.csv"

            # Check if the file exists
            file_exists = os.path.isfile(csv_file)

            # Define headers
            headers = [
                "Regno", "proj_name", "promoter_type", "proj_district", "prom_name", "project_type",
                "project_comp_date", "proj_status", "project_address", "inventory_type",
                "carpet_area", "terrace_area", "no_of_inventory", "balcony_area", "arch_name",
                "num_projects_completed", "total_flats_value", "occupancy_date_value"
            ]

            # Data to append
            row_data = [
                xid, proj_name, promoter_type, proj_district, prom_name, project_type,
                project_comp_date, proj_status, project_address, inventory_type,
                carpet_area, terrace_area, no_of_inventory, balcony_area, arch_name,
                num_projects_completed, total_flats_value, occupancy_date_value
            ]
            print(row_data)

            # Open the CSV file in append mode
            with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                
                # Write the header if the file doesn't exist
                if not file_exists:
                    writer.writerow(headers)
                
                # Write the data row
                writer.writerow(row_data)

            print(f"Data successfully saved to {csv_file}")

            
            driver.back()
                
            
        except:
            #driver.back()
            continue
        print("HERE1")
        
        
          
              
                   

 
         

