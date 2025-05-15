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

 
with open("gujrat-focus.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
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
            project_name = driver.find_element(By.XPATH, "(//h2[@class='title'])[1]").text
            project_land_area = driver.find_element(By.XPATH, "//p[contains(text(),'Project Land Area (Sq Mtrs)')]/strong").text
            total_open_area = driver.find_element(By.XPATH, "//p[contains(text(),'Total Open Area (Sq Mtrs)')]/strong").text
            project_address = driver.find_element(By.XPATH, "//p[contains(text(),'Project Address')]/strong").text
            project_end_date = driver.find_element(By.XPATH, "//p[contains(text(),'Project End Date')]/strong").text
            project_type = driver.find_element(By.XPATH, "//p[contains(text(),'Type')]/strong").text
            #gujrera_certificate = driver.find_element(By.XPATH, "//h6[contains(text(),'GujRERA Certificate Project')]").text
            #scan_for_details = driver.find_element(By.XPATH, "//h6[contains(text(),'Scan For Project Details')]").text
            total_units = driver.find_element(By.XPATH, "//p[contains(text(),'Total Units')]/strong").text
            total_towers_blocks = driver.find_element(By.XPATH, "//p[contains(text(),'Total No. of Towers/Blocks')]/strong").text

            # certificate_img = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, 'certificateImg'))
            # )
            # certificate_img.click()
            # time.sleep(2)
            # download_and_rename_pdf(driver, fileName, "GujRERA_Certificate", download_dir)
            # time.sleep(6)
        except:
            pass


        # # Download QR Code
        # try:
        #     # Locate the QR code image
        #     element = driver.find_element(By.CLASS_NAME, 'qrcode')
        #     element.screenshot("qr.png")
        #     time.sleep(2)
        #     # Ensure the directory exists
        #     qr_codes_dir = "QR_codes"
        #     os.makedirs(qr_codes_dir, exist_ok=True)

        #     # Save the QR code screenshot
        #     old_file_path = "qr.png"
        #     new_file_path = os.path.join(qr_codes_dir, f"{fileName}_QR.png")

        #     # Check if the file already exists in the new file path
        #     if os.path.exists(new_file_path):
        #         print(f"File {new_file_path} already exists. Deleting from current directory and doing nothing.")
        #         os.remove(old_file_path)
        #     else:
        #         # Rename the file
        #         os.rename(old_file_path, new_file_path)
        #         print(f"QR code saved successfully: {new_file_path}")

        #     time.sleep(3)

        # except Exception as e:
        #     print(f"Error saving QR code: {e}")

        # try:
        #     commencement_certificate_button = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[2]/div/div[2]/div/div/div[10]/div[3]/app-file-view/a/img[2]')
        #     commencement_certificate_button.click()
            
        #     download_and_rename_pdf(driver, fileName, "commencement_certificate", download_dir)

        # except:
        #     pass 
 

        # try:
        #     approved_layout_plan_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-tabContent']/div[1]/div[2]/div/div[2]/div/div/div[1]/div[3]/app-file-view/a/img[2]"))
        #     )
        #     approved_layout_plan_button.click()
        #     download_and_rename_pdf(driver, fileName, "approved_layout_plan", download_dir)
        # except Exception as e:
        #     print(f"Error clicking approved_layout_plan_button: {e}")

        # try:
        #     land_doc_loc_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-tabContent']/div[1]/div[2]/div/div[2]/div/div/div[2]/div[3]/app-file-view/a/img[2]"))
        #     )
        #     land_doc_loc_button.click()
        #     download_and_rename_pdf(driver, fileName, "land_doc_loc", download_dir)
        # except Exception as e:
        #     print(f"Error clicking land_doc_loc_button: {e}")

        # try:
        #     approved_build_plot_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-tabContent']/div[1]/div[2]/div/div[2]/div/div/div[3]/div[3]/app-file-view/a/img[2]"))
        #     )
        #     approved_build_plot_button.click()
        #     download_and_rename_pdf(driver, fileName, "approved_build_plot_button", download_dir)

        # except:
        #     pass

         

        # try:
        #     Brochure_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='nav-tabContent']/div[1]/div[2]/div/div[2]/div/div/div[5]/div[3]/app-file-view/a/img[2]"))
        #     )
        #     Brochure_button.click()

        #     download_and_rename_pdf(driver, fileName, "brochure", download_dir)

        # except:
        #     pass
        
        # try:
        #     approved_section_plan_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="collapseOne"]/div/div/div[3]/div/app-file-view/a/img[2]'))
        #     )
        #     approved_section_plan_button.click()

        #     download_and_rename_pdf(driver, fileName, "approved_section_plan", download_dir)

        # except:
        #     pass 

        
        # try:
        #     area_devlopment_plan_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='collapseOne']/div/div/div[4]/div/app-file-view/a/img[2]"))
        #     )
        #     area_devlopment_plan_button.click()
            
        #     download_and_rename_pdf(driver, fileName, "area_develop_plan", download_dir)

        # except:
        #     pass 

        # try:
        #     project_spefication_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[2]/div/div[2]/div/div/div[6]/div[3]/app-file-view/a/img[2]'))
        #     )
        #     project_spefication_button.click()
            
        #     download_and_rename_pdf(driver, fileName, "project_specification", download_dir)

        # except:
        #     pass 

        # try:
        #     Draft_Brochure_plan_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, "//*[@id='collapseOne']/div/div/div[5]/div/app-file-view/a/img[2]"))
        #     )
        #     Draft_Brochure_plan_button.click()

        #     download_and_rename_pdf(driver, fileName, "Draft_Brochure", download_dir)

        # except:
        #     pass 

        # try:
        #     #opening technical details on webpage
        #     technical_details_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="headingOne"]/h5/button'))
        #     )
        #     technical_details_button.click()

        #     project_photo_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="collapseOne"]/div/div/div[7]/div/app-file-view/a/img[2]'))
        #     )
        #     project_photo_button.click()

        #     download_and_rename_pdf(driver, fileName, "Project Photo", download_dir)

        # except:
        #     pass


        
        # try:
        #     #opening financial details on webpage
        #     financial_details_button = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="headingThree"]/h5/button'))
        #     )
        #     financial_details_button.click()

        #     Balance_sheet_button1 = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="collapseThree"]/div/div[2]/div[1]/div/app-file-view/a/img[2]'))
        #     )
        #     Balance_sheet_button1.click()

        #     download_and_rename_pdf(driver, fileName, "Balance_sheet1", download_dir)

        # except:
        #     pass

        # try:
        #     Balance_sheet_button2 = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="collapseThree"]/div/div[2]/div[2]/div/app-file-view/a/img[2]'))
        #     )
        #     Balance_sheet_button2.click()

        #     download_and_rename_pdf(driver, fileName, "Balance_sheet2", download_dir)

        # except:
        #     pass

        # try:
        #     Balance_sheet_button3 = WebDriverWait(driver, 10).until(
        #         EC.element_to_be_clickable((By.XPATH, '//*[@id="collapseThree"]/div/div[2]/div[3]/div/app-file-view/a/img[2]'))
        #     )
        #     Balance_sheet_button3.click()

        #     download_and_rename_pdf(driver, fileName, "Balance_sheet3", download_dir)

        # except:
        #     pass

        try:
            pool_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[1]/div/div[1]')
            pool_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[1]/div/div[2]/p').text
            pool_class = pool_image.get_attribute("class")
            pool_Avaliable = "No" if "img-disabled" in pool_class else "Yes"

            disposalOfSewageWater_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[2]/div/div[1]')
            disposalOfSewageWater_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[2]/div/div[2]/p').text
            disposalOfSewageWater_class = disposalOfSewageWater_image.get_attribute("class")
            disposalOfSewageWater_Avaliable = "No" if "img-disabled" in disposalOfSewageWater_class else "Yes"

            lift_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[3]/div/div[1]')
            lift_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[3]/div/div[2]/p').text
            lift_class = lift_image.get_attribute("class")
            lift_Avaliable = "No" if "img-disabled" in lift_class else "Yes"

            garden_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[4]/div/div[1]')
            garden_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[4]/div/div[2]/p').text
            garden_class = garden_image.get_attribute("class")
            garden_Avaliable = "No" if "img-disabled" in garden_class else "Yes"

            security_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[5]/div/div[1]')
            security_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[5]/div/div[2]/p').text
            security_class = security_image.get_attribute("class")
            security_Avaliable = "No" if "img-disabled" in security_class else "Yes"

            drinkingWater_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[6]/div/div[1]')
            drinkingWater_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[2]/div[6]/div/div[2]/p').text
            drinkingWater_class = drinkingWater_image.get_attribute("class")
            drinkingWater_Avaliable = "No" if "img-disabled" in drinkingWater_class else "Yes"

            waterConservation_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[1]/div/div[1]')
            waterConservation_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[1]/div/div[2]/p').text
            waterConservation_class = waterConservation_image.get_attribute("class")
            waterConservation_Avaliable = "No" if "img-disabled" in waterConservation_class else "Yes"

            waterSupply_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[2]/div/div[1]')
            waterSupply_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[2]/div/div[2]/p').text
            waterSupply_class = waterSupply_image.get_attribute("class")
            waterSupply_Avaliable = "No" if "img-disabled" in waterSupply_class else "Yes"

            renewableEnergy_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[3]/div/div[1]')
            renewableEnergy_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[3]/div/div[2]/p').text
            renewableEnergy_class = renewableEnergy_image.get_attribute("class")
            renewableEnergy_Avaliable = "No" if "img-disabled" in renewableEnergy_class else "Yes"

            communityHall_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[4]/div/div[1]')
            communityHall_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[4]/div/div[2]/p').text
            communityHall_class = communityHall_image.get_attribute("class")
            communityHall_Avaliable = "No" if "img-disabled" in communityHall_class else "Yes"

            fireSafety_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[5]/div/div[1]')
            fireSafety_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[5]/div/div[2]/p').text
            fireSafety_class = fireSafety_image.get_attribute("class")
            fireSafety_Avaliable = "No" if "img-disabled" in fireSafety_class else "Yes"

            road_image = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[6]/div/div[1]')
            road_text = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[1]/div[4]/div/div/div[3]/div[6]/div/div[2]/p').text
            road_class = road_image.get_attribute("class")
            road_Avaliable = "No" if "img-disabled" in road_class else "Yes"

        except:
            print("Error extracting amenities data.")


        try:
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[@id="nav-tab"]/a[2]').click()
            promoter_name = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[2]/div[1]/div/div/div[2]/div[1]/p[1]/span').text
            promoter_type = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[2]/div[1]/div/div/div[2]/div[1]/p[2]/span').text
            # Extract "Total no. Of Years Of Work Experience Of Group Entity In Gujarat"
            work_experience_in_gujarat = wait.until(EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Total no. Of Years Of Work Experience Of Group Entity In Gujarat:')]//following-sibling::span"))).text

            # Extract "Total no. Of Completed Projects By Group Entity"
            completed_projects = wait.until(EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Total no. Of Completed Projects By Group Entity:')]//following-sibling::span"))).text

 
        except:
            work_experience_in_gujarat = ""
            completed_projects = ""
        

            # Check if the <h3> tag contains 'Architects'
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
            driver.find_element(By.XPATH, '//*[@id="nav-tab"]/a[3]').click()
            time.sleep(5)

            # Find the table
            table_xpath = "//*[@id=\"nav-tabContent\"]/div[3]/div[1]/div/div/div[4]/div/div/div[4]/div/div/table[1]"
            table = driver.find_element(By.XPATH, table_xpath)

            # Extract table headers
            headers = [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]

            # Extract table rows
            data = []
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:  # Skip the header row
                cols = row.find_elements(By.TAG_NAME, "td")
                data.append([col.text.strip() for col in cols])

            # Append registration number (assuming it's a single column addition)
            registration_number = xid  # Replace with actual registration number
            for row in data:
                row.insert(0, registration_number)

            # Define CSV file
            csv_file = "booking_details.csv"

            # Check if file exists and is non-empty
            file_exists = os.path.exists(csv_file) and os.stat(csv_file).st_size > 0

            # Write data to CSV
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["Registration Number"] + headers)  # Write headers if file is new or empty
                writer.writerows(data)
            print(f"Data written to {csv_file}.")

        except:
            pass

        
        
        '''try:
            time.sleep(10)
            driver.find_element(By.XPATH, '//*[@id="nav-tab"]/a[3]').click();
            time.sleep(10)
            getLenbody = driver.find_elements(By.XPATH, '//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody')
            setLenbody = len(getLenbody)+1
             
            for x in range(1, setLenbody):
                 
                for tr in range(1,4):
                    print(tr)
                    if tr==1:
                        block_name = driver.find_element(By.XPATH, '//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody['+str(x)+']/tr[1]/td').text
                        print(block_name)
                        continue
                    else:
                        td1=driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody['+str(x)+']/tr['+str(tr)+']/td[1]').text
                        print(td1)
                        td2=driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody['+str(x)+']/tr['+str(tr)+']/td[2]').text
                        td3=driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody['+str(x)+']/tr['+str(tr)+']/td[3]').text
                        td4=driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[3]/div[1]/div/div/div[4]/div/div/div[8]/div/div/table/tbody['+str(x)+']/tr['+str(tr)+']/td[4]').text
                        
                    block_data= block_name + ';' + td1 +':'+td2+';'+td3 +':'+td4+';'

                    print(block_data)
                    
        except:
            pass'''
        try:
            # Prepare data to be written to CSV
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
                promoter_type,
                work_experience_in_gujarat,
                completed_projects,
                Architects_name, 
                f"{pool_text}: {pool_Avaliable}",
                f"{disposalOfSewageWater_text} {disposalOfSewageWater_Avaliable}",
                f"{lift_text}: {lift_Avaliable}",
                f"{garden_text}: {garden_Avaliable}",
                f"{security_text}: {security_Avaliable}",
                f"{drinkingWater_text}: {drinkingWater_Avaliable}",
                f"{waterConservation_text}: {waterConservation_Avaliable}",
                f"{waterSupply_text}: {waterSupply_Avaliable}",
                f"{renewableEnergy_text}: {renewableEnergy_Avaliable}",
                f"{communityHall_text}: {communityHall_Avaliable}",
                f"{fireSafety_text}: {fireSafety_Avaliable}",
                f"{road_text}: {road_Avaliable}"
            ]

            # Open the file in append mode and write data row-wise
            with open("gujrat_project_details.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                
                # If the file is empty, write the header (field names)
                if file.tell() == 0:
                    writer.writerow(["Reg. No.", "Project Name", "Project Land Area (Sq Mtrs)", 
                                     "Total Open Area (Sq Mtrs)", "Project Address", "Project End Date", 
                                     "Type", "Total Units", "Total No. of Towers/Blocks","Promoter name", "Promoter Type", "Total no. Of Years Of Work Experience Of Group Entity In Gujarat",
                                     "Total no. Of Completed Projects By Group Entity",
                                     "Architect Name", "Pool Avaliable", "Disposal Of Sewage Water Avaliable", "Lift Avaliable", "Garden Avaliable", "Security Avaliable", "Drinking Water Avaliable", "Water Conservation Avaliable", "Water Supply Avaliable", "Renewable Energy Avaliable", "Community Hall Avaliable", "Fire Safety Avaliable", "Road Avaliable"
                                     ])

                # Write the data as a single row (horizontal layout)
                writer.writerow(data)

            print("Data has been appended to 'gujrat_project_details.csv'.")


            
            #driver.back()
                
            
        except:
            #driver.back()
            continue

















