from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService, Service
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
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#chrome_options = webdriver.ChromeOptions() 

#chrome_options = webdriver.ChromeOptions() 

# Setup Download Folder
download_folder = os.path.abspath("pdf")
os.makedirs(download_folder, exist_ok=True)

# Setup Chrome Options
options = Options()
options.add_experimental_option("prefs", {
    "download.default_directory": download_folder,  # Set download directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,  # Prevents opening PDFs in-browser
    "profile.default_content_settings.popups": 0,
})

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
def move_and_rename_last_download(download_dir, new_file_name):
    """
    Moves the last downloaded file from the default Downloads folder to a specified directory 
    and renames the file.
    
    :param download_dir: The target directory to move the file to.
    :param new_file_name: The new name for the downloaded file.
    """
    # Path to the default Downloads directory (Change if needed)
    default_downloads_dir = os.path.expanduser("~/Downloads")
    
    # List all files in the Downloads folder sorted by modification time (newest first)
    downloaded_files = sorted(
        (f for f in os.listdir(default_downloads_dir) if os.path.isfile(os.path.join(default_downloads_dir, f))),
        key=lambda f: os.path.getmtime(os.path.join(default_downloads_dir, f)),
        reverse=True
    )
    
    # Ensure there is at least one file
    if not downloaded_files:
        print("No files found in the Downloads folder.")
        return

    # The last downloaded file
    last_downloaded_file = downloaded_files[0]
    
    # Full path of the last downloaded file
    source_file_path = os.path.join(default_downloads_dir, last_downloaded_file)
    
    # Check if the file is still downloading (Chrome creates .crdownload files)
    if last_downloaded_file.endswith(".crdownload"):
        print("Download still in progress, waiting for completion.")
        time.sleep(1)
        return move_and_rename_last_download(download_dir, new_file_name)  # Recurse to check again
    
    # Target path in the desired directory with the new name
    target_file_path = os.path.join(download_dir, new_file_name)
    
    # Move and rename the file
    try:
        shutil.move(source_file_path, target_file_path)
        print(f"Moved and renamed file to {target_file_path}")
    except Exception as e:
        print(f"Error while moving or renaming the file: {e}")

def download_and_rename_pdf(driver, project_name, file_type, download_dir):
    """
    Triggers file download via Selenium, and renames it dynamically based on project_name.
    
    :param driver: The Selenium WebDriver instance.
    :param project_name: The name of the project to use in the filename.
    :param file_type: The type of the file (e.g., 'GujRERA_Certificate').
    :param download_dir: Directory where the file is saved.
    """
    # Simulate clicking the download button or link to trigger the download
    try:
        # Locate the download link or button by XPath (Modify as per the actual page structure)
        #download_button = driver.find_element(By.XPATH, xpth)
            
        #download_button.click()
        wait = WebDriverWait(driver, 10)

        # Wait until the modal with the class "fade show" is visible and interactable
        modal = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal fade show')]")))

        # Wait for the "Download" button within the modal to be clickable
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Download']")))

        # Optionally, print modal title for confirmation
        modal_title = modal.find_element(By.XPATH, ".//div[contains(@class, 'modal-header')]//h4").text
        print(f"Modal Title: {modal_title}")

        # Click the download button
        ActionChains(driver).move_to_element(download_button).click().perform()
        print(f"Downloading {file_type}...")
        download_dir = os.path.join(os.getcwd(), "downloaded_pdfs") # Current directory (can change to your custom directory)
        
        new_file_name = f"{project_name}_{file_type}.pdf"  # New name for the file

        move_and_rename_last_download(download_dir, new_file_name)
        # Wait for the file to download (increase the time if necessary)
       
        print(f"{file_type} renamed to {new_file_name}")
        close_button = modal.find_element(By.XPATH, ".//button[@class='close']")
        close_button.click()
    except Exception as e:
        print(f"Error while downloading or renaming {file_type}: {e}")

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

        
        time.sleep(3)  # Let page load

         # Extract text
        try:
            text_element = driver.find_element(By.XPATH, '//*[@id="Documents"]/div/div[3]/div[2]/div/div[1]/p1')
            text_value = text_element.text.strip()
            print(f"Extracted text: {text_value}")
        except Exception as e:
            print(f"Error extracting text: {e}")
            text_value = "unknown"

        # Extract PDF link
        try:
            link_element = driver.find_element(By.XPATH, '//*[@id="Documents"]/div/div[3]/div[2]/div/div[2]/p/a')
            pdf_url = link_element.get_attribute("href")
            print(f"Extracted PDF URL: {pdf_url}")
        except Exception as e:
            print(f"Error extracting PDF link: {e}")
            driver.quit()
            exit()

        # Open a new window and switch to it
        try:
            driver.execute_script("window.open('', '_blank');")
            driver.switch_to.window(driver.window_handles[1])
            print("New window opened successfully.")
        except Exception as e:
            print(f"Error opening new window: {e}")
            # driver.quit()
            # exit()

        # Download the PDF
        try:
            # driver.get(pdf_url)
            # print("PDF download started.")
            # time.sleep(20)  # Wait for the download to complete
            download_and_rename_pdf(driver, text_value, "Tamilnadu", download_folder)
        except Exception as e:
            print(f"Error downloading PDF: {e}")
        
        # Close the new window
        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[1])
            print("Closed the new window and switched back.")
        except Exception as e:
            print(f"Error closing the new window: {e}")

        # Rename the downloaded file
        try:
            downloaded_files = os.listdir(download_folder)
            if downloaded_files:
                latest_file = max(
                    [os.path.join(download_folder, f) for f in downloaded_files], key=os.path.getctime
                )
                new_filename = os.path.join(download_folder, f"regnumber_{text_value}.pdf")
                os.rename(latest_file, new_filename)
                print(f"PDF saved as {new_filename}")
            else:
                print("No downloaded files found.")
        except Exception as e:
            print(f"Error renaming PDF file: {e}")

        

        # List of labels you want to fetch
        labels_to_find = [
            "Project Name :",
            "Project Details :",
            "Type of Building :",
            "Usage :",
            "Site Extent(Sq.m) :",
            "Total No. of Dwelling Units including all Phases/Villas :",
            "Stage of Construction :",
            "Project Completion Date :",
            "Latitude :",
            "Longitude :"
        ]

        # Find the "Proposed Project Detail" header
        header = driver.find_element(By.XPATH, "//span[contains(text(), 'Proposed Project Detail')]")

        # Find all rows under this header section that contain the required labels
        rows = header.find_elements(By.XPATH, "//following-sibling::div[contains(@class, 'form_sec')]//div[contains(@class, 'form-group')]")

        # Create an empty dictionary to store the scraped data
        

        # Loop through each row and extract the label (p1) and its corresponding value (p)
        for row in rows:
            try:
                # Extract the label and value
                label = row.find_element(By.XPATH, ".//p1").text.strip()
                 
                # Check if the label is in the list of labels_to_find
                if label in labels_to_find:
                    # Extract the value corresponding to the label
                    value = row.find_element(By.XPATH, ".//p").text.strip()
                    
                    # Add the label and value to the dictionary
                    project_details[label] = value
            except Exception as e:
                print(f"Error while extracting data:")

        # Print the extracted project details
        #print(project_details)
         
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









