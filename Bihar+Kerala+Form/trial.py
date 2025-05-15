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
import openpyxl, requests
from openpyxl.workbook import Workbook
from selenium.common.exceptions import NoSuchElementException
import csv
import pdb
from io import BytesIO
from datetime import date

#chrome_options = webdriver.ChromeOptions() 
chrome_options = Options()
download_dir = "downloaded_pdfs"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set the download directory
        "download.prompt_for_download": False,        # Disable download prompt
        "download.directory_upgrade": True,           # Allow directory change
        "safebrowsing.enabled": True                  # Enable safe browsing
    })
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://world.einnews.com/all_rss")
driver.maximize_window()

element = driver.find_element(By.XPATH, '/html/body/p/a').click()


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

def extract_amenities(driver, gujrera_reg_no):
    """
    Extracts the amenities listed under the "Common Amenities" section on the page and writes them to a CSV file.
    
    :param driver: The Selenium WebDriver instance.
    :param gujrera_reg_no: The registration number of the project.
    """
    amenities = []
    try:
        # Wait until the "Common Amenities" section is present
        # wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Common Amenities')]")))

        # Iterate through the range of possible values for the last div[] in the XPath
        for i in range(1, 13):
            # try:
            # Check if the image element does not have the class 'img disabled'
                # image_element = driver.find_element(By.XPATH, f'//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[{i}]/div/div[1]')
                # if 'img disabled' not in image_element.get_attribute('class'):
                    # Locate the amenity element using the updated XPath
            amenity_element = driver.find_element(By.XPATH, f'//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[{i}]/div/div[2]/p')
            amenities.append(amenity_element.text.strip())
            # except NoSuchElementException:
            #     # If the element is not found, break the loop
            #     break

        print("Amenities extracted:", amenities)

        # Write the amenities to the CSV file
        with open("gujarat_rera_amenities.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            
            # If the file is empty, write the header (field names)
            if file.tell() == 0:
                writer.writerow(["Reg. No.", "Amenity"])

            # Write each amenity as a separate row
            for amenity in amenities:
                # writer.writerow([gujrera_reg_no, amenity])
                writer.writerow([amenity])

        print("Amenities have been appended to 'gujarat_rera_amenities.csv'.")
    except Exception as e:
        print(f"Error while extracting amenities: {e}")
    
c=0
x=1
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
time.sleep(5)





with open("gujrat-focus.csv", "r") as csvfile:
    records = csv.reader(csvfile, delimiter=",")
    next(records)
    for row in records:
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
            if(driver.find_element(By.ID, 'loginModal')):
                time.sleep(3)
                driver.get("https://gujrera.gujarat.gov.in/#/home")
                time.sleep(5)
            else:
                if(driver.find_element(By.CSS_SELECTOR, '#loginModal > div > div > div.modal-header > h4')):
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


        try:
            
            gujrera_reg_no = xid
            project_name = driver.find_element(By.XPATH, "(//h2[@class='title'])[1]").text
            project_land_area = driver.find_element(By.XPATH, "//p[contains(text(),'Project Land Area (Sq Mtrs)')]/strong").text
            total_open_area = driver.find_element(By.XPATH, "//p[contains(text(),'Total Open Area (Sq Mtrs)')]/strong").text
            project_address = driver.find_element(By.XPATH, "//p[contains(text(),'Project Address')]/strong").text
            project_end_date = driver.find_element(By.XPATH, "//p[contains(text(),'Project End Date')]/strong").text
            project_type = driver.find_element(By.XPATH, "//p[contains(text(),'Type')]/strong").text
            total_units = driver.find_element(By.XPATH, "//p[contains(text(),'Total Units')]/strong").text
            total_towers_blocks = driver.find_element(By.XPATH, "//p[contains(text(),'Total No. of Towers/Blocks')]/strong").text

            # Extracting the required details using XPaths
            extract_amenities(driver, gujrera_reg_no)

            driver.find_element(By.CLASS_NAME, 'certificateImg').click()
            time.sleep(2)
            download_and_rename_pdf(driver, fileName, "GujRERA_Certificate", download_dir)

            
        except:
            pass

        try:
            approved_layout_plan_button = driver.find_element(By.XPATH, "//span[contains(text(),'Approved Layout Plan')]/parent::div//img[contains(@src, 'view.png')]")
            ActionChains(driver).move_to_element(approved_layout_plan_button).click().perform()

            download_and_rename_pdf(driver, fileName, "approved_layout_plan", download_dir)
        except:
            pass

        try:
            land_doc_loc_button = driver.find_element(By.XPATH, "//span[contains(text(),'Land documents & Location')]/parent::div//img[contains(@src, 'view.png')]")
            ActionChains(driver).move_to_element(land_doc_loc_button).click().perform()

            download_and_rename_pdf(driver, fileName, "land_doc_loc", download_dir)
        except:
            pass

        try:
            approved_build_plot_button = driver.find_element(By.XPATH, "//span[contains(text(),'Approved Building/Plotting Plan')]/parent::div//img[contains(@src, 'view.png')]")
            ActionChains(driver).move_to_element(approved_build_plot_button).click().perform()
            download_and_rename_pdf(driver, fileName, "approved_build_plot_button", download_dir)
        except:
            pass

        try:
            Brochure_button = driver.find_element(By.XPATH, "//span[contains(text(),'Brochure')]/parent::div//img[contains(@src, 'view.png')]")
            ActionChains(driver).move_to_element(Brochure_button).click().perform()

            download_and_rename_pdf(driver, fileName, "brochure", download_dir)
        except:
            pass

        try:
            approved_section_plan_button = driver.find_element(By.XPATH, "//a[.//img[@alt='File view icon'] and .//span[contains(text(), 'Approved Section Plan/ Infrastructure Plan')]]//img[@alt='File view icon']")
            ActionChains(driver).move_to_element(approved_section_plan_button).click().perform()

            download_and_rename_pdf(driver, fileName, "approved_section_plan", download_dir)
        except:
            pass

        try:
            area_devlopment_plan_button = driver.find_element(By.XPATH, "//a[.//img[@alt='File view icon'] and .//span[contains(text(), 'Area Development Plan')]]//img[@alt='File view icon']")
            ActionChains(driver).move_to_element(area_devlopment_plan_button).click().perform()

            download_and_rename_pdf(driver, fileName, "area_develop_plan", download_dir)
        except:
            pass

        try:
            Draft_Brochure_plan_button = driver.find_element(By.XPATH, "//a[.//img[@alt='File view icon'] and .//span[contains(text(), 'Draft Brochure')]]//img[@alt='File view icon']")
            ActionChains(driver).move_to_element(Draft_Brochure_plan_button).click().perform()

            download_and_rename_pdf(driver, fileName, "Draft_Brochure", download_dir)
        except:
            pass

        try:
            Balance_sheet_button = driver.find_element(By.XPATH, "//a[.//img[@alt='File view icon'] and .//span[contains(text(), 'Balance sheet')]]//img[@alt='File view icon']")
            ActionChains(driver).move_to_element(Balance_sheet_button).click().perform()

            download_and_rename_pdf(driver, fileName, "Balance_sheet", download_dir)
        except:
            pass

        try:
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[@id="nav-tab"]/a[2]').click()
            promoter_name = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[2]/div[1]/div/div/div[2]/div[1]/p[1]/span').text
            # Extract "Total no. Of Years Of Work Experience Of Group Entity In Gujarat"
            work_experience_in_gujarat = wait.until(EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Total no. Of Years Of Work Experience Of Group Entity In Gujarat:')]//following-sibling::span"))).text

            # Extract "Total no. Of Completed Projects By Group Entity"
            completed_projects = wait.until(EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Total no. Of Completed Projects By Group Entity:')]//following-sibling::span"))).text
        except:
            work_experience_in_gujarat = ""
            completed_projects = ""

        try:
            if wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Architects')]"))):
                # Extract the "Name" text from the associated <p> tag
                Architects_name = wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Architects')]//following::p[1]//strong[text()='Name:']//following-sibling::text()"))).strip()
                
                # Print the extracted name
                print(f"Architect Name: {Architects_name}")
            else:
                print("Architect section not found.")
        except:
            Architects_name = ""

        try:
            # # Extract amenities and write to CSV
            # extract_amenities(driver, gujrera_reg_no)

            # Prepare data to be written to another CSV
            data = [
                gujrera_reg_no,
                project_name,
                project_land_area,
                total_open_area,
                project_address,
                project_end_date,
                project_type,
                total_units,
                total_towers_blocks,
                promoter_name,
                work_experience_in_gujarat,
                completed_projects,
                Architects_name
            ]

            # Open the file in append mode and write data row-wise
            with open("gujrat_project_details.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                
                # If the file is empty, write the header (field names)
                if file.tell() == 0:
                    writer.writerow(["Reg. No.", "Project Name", "Project Land Area (Sq Mtrs)", 
                                     "Total Open Area (Sq Mtrs)", "Project Address", "Project End Date", 
                                     "Type", "Total Units", "Total No. of Towers/Blocks", "Promoter name", 
                                     "Total no. Of Years Of Work Experience Of Group Entity In Gujarat",
                                     "Total no. Of Completed Projects By Group Entity", "Architect Name"])

                # Write the data as a single row (horizontal layout)
                writer.writerow(data)

            print("Data has been appended to 'gujrat_project_details.csv'.")
        except:
            continue

















