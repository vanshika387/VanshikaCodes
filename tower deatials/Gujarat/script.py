from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
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
import openpyxl, requests
from openpyxl.workbook import Workbook
from selenium.common.exceptions import NoSuchElementException
import csv
import pdb
from io import BytesIO
from datetime import date
import pyautogui

# Set up Chrome options to download files to a specific directory
chrome_options = Options()
download_dir = os.path.join(os.getcwd(), "downloaded_pdfs")  # Current directory (can change to your custom directory)
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
temp_download_dir = os.path.join(os.getcwd(), "temp_downloads")
if not os.path.exists(temp_download_dir):
    os.makedirs(temp_download_dir)
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": temp_download_dir,  # Set the download directory
    "download.prompt_for_download": False,            # Disable download prompt
    "download.directory_upgrade": True,               # Allow directory change
    "safebrowsing.enabled": True                      # Enable safe browsing
})
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://gujrera.gujarat.gov.in/#/home")
driver.maximize_window()

ids_group = []
cnt = 0
cc="NO"
c=0

wait = WebDriverWait(driver, 10)
def move_and_rename_last_download(download_dir, new_file_name):
    """
    Moves the last downloaded file from the default Downloads folder to a specified directory 
    and renames the file.
    
    :param download_dir: The target directory to move the file to.
    :param new_file_name: The new name for the downloaded file.
    """
    # Path to the default Downloads directory (Change if needed)
    
    default_downloads_dir = os.path.join(os.getcwd(), "temp_downloads")  # Creates a temp folder in the script directory
    if not os.path.exists(default_downloads_dir):
        os.makedirs(default_downloads_dir)
    
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
    
    # Check if the file already exists in the download directory
    if os.path.exists(target_file_path):
        print(f"File {new_file_name} already exists in {download_dir}. Deleting from temporary and doing nothing.")
        os.remove(source_file_path)
    else:
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
        time.sleep(30)
        download_dir = os.path.join(os.getcwd(), "downloaded_pdfs") # Current directory (can change to your custom directory)
        
        new_file_name = f"{project_name}_{file_type}.pdf"  # New name for the file

        move_and_rename_last_download(download_dir, new_file_name)
        # Wait for the file to download (increase the time if necessary)
       
        print(f"{file_type} renamed to {new_file_name}")
        close_button = modal.find_element(By.XPATH, ".//button[@class='close']")
        close_button.click()
    except Exception as e:
        print(f"Error while downloading or renaming {file_type}: {e}")
def notFound():
    try:
        time.sleep(5)
        if(driver.find_element(By.CSS_SELECTOR,'#loginModal > div > div > div.modal-body > div > div').text == 'No Records Found.'):
            time.sleep(2)
            driver.find_element(By.CSS_SELECTOR,'/#loginModal > div > div > div.modal-footer > button').click()
            return True
        else:
            return True
             

    except:
        driver.find_element(By.CSS_SELECTOR, '#loginModal > div > div > div.modal-footer > button').click()
        time.sleep(5)
         
def check_exists_by_xpath(xpath):
    try:
        driver.find_element(By.CLASS_NAME,xpath).click()
        return True
    except:
        time.sleep(10)
        check_exists_by_xpath(xpath)
    
c=0
x=1
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
time.sleep(5)

 
with open("gujarat/focus2.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
    for row in records:
        try: 
            # xid_temp = row[0]
            xid = row[0]
            print(xid)
            driver.find_element(By.XPATH, '//*[@id="validateFoem"]/div/input').send_keys(Keys.CONTROL, 'a')
            driver.find_element(By.XPATH, '//*[@id="validateFoem"]/div/input').send_keys(xid)

            fileName = xid.replace(r'/', '-')
            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB)
            actions.send_keys(Keys.ENTER)
            try:
                actions.perform()
            except:
                pass
            time.sleep(5)
            try:
                
                if(driver.find_element(By.ID,'loginModal')):
                    #(driver.find_element(By.CSS_SELECTOR,'#loginModal > div > div > div.modal-body > div > div').text == 'No Records Found.'):
                    time.sleep(3)
                    driver.get("https://gujrera.gujarat.gov.in/#/home")
                    time.sleep(5)
                else:
                    if(driver.find_element(By.CSS_SELECTOR,'#loginModal > div > div > div.modal-header > h4')):
                        driver.get("https://gujrera.gujarat.gov.in/#/home")
                        time.sleep(5)
                continue
                    
                    
            except:
                pass
                
            try:
                check_exists_by_xpath("vmore")
            except:
                driver.find_element(By.CSS_SELECTOR, "#innerHome > app-search-view > div > div > div:nth-child(3) > div.row.flexrow-5 > div > div > div > a").click()
            else:
                pass
            time.sleep(3)
            #//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody/tr[2]/td[3]
            try:
                # Extracting the required details using XPaths
                gujrera_reg_no = xid
            except:
                pass

            try: 
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@id="nav-tab"]/a[3]').click()
                try:
                    # Locate the table
                    table = driver.find_element(By.CLASS_NAME, "table.table-bordered.form3TableAll")
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    # Open the CSV file in append mode
                    with open("gujarat/blockBookingDetails2.csv", mode="a", newline="") as file:
                        writer = csv.writer(file)

                        # Write the header only if the file is empty
                        if file.tell() == 0:
                            header = ["Rera No."] + [th.text for th in rows[0].find_elements(By.TAG_NAME, "th")]
                            writer.writerow(header)

                        # Iterate through table rows and write data
                        for row in rows[1:]:  # Skip the header row
                            data = [xid] + [td.text for td in row.find_elements(By.TAG_NAME, "td")]
                            writer.writerow(data)

                    print(f"Data from table saved to 'blockBookingDetails.csv' for xid: {xid}")

                except Exception as e:
                    print(f"Error extracting table data: {e}")
            except:
                pass

                # Check if the <h3> tag contains 'Architects'
        except Exception as e:
            print("Error processing ID:", xid, "Error:", e)
            continue