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
 
options = Options()
download_dir = "mypdf"
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
 
options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Set the download directory
        "download.prompt_for_download": False,        # Disable download prompt
        "download.directory_upgrade": True,           # Allow directory change
        "safebrowsing.enabled": True                  # Enable safe browsing
    })

#driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver = webdriver.Chrome(options=options)
driver.get("https:/rerait.telangana.gov.in/SearchList/Search")
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
 

with open("tel-focus.csv","r") as csvfile:
    records  = csv.reader(csvfile,delimiter=",")
    next(records)
    #pdb.set_trace()
    for row in records:
        time.sleep(5)
        reg_no = row[0]
        print(reg_no)
        project_details = {}
        project_details['reg_no'] = reg_no
         
        time.sleep(2)
        driver.find_element(By.ID, 'CertiNo').send_keys(Keys.CONTROL, 'a')
        driver.find_element(By.ID, 'CertiNo').send_keys(reg_no)
        driver.find_element(By.ID, 'btnSearch').click()


        fileName = reg_no.replace(r'/', '-')

        time.sleep(5)
        try:
            project_details['Project_Name'] = getText('//*[@id="gridview"]/div[1]/div/table/tbody/tr/td[2]')
            project_details['Promoter_Name'] = getText('//*[@id="gridview"]/div[1]/div/table/tbody/tr/td[3]')
            '''           
            try:
                driver.find_element(By.XPATH, '//*[@id="gridview"]/div[1]/div/table/tbody/tr/td[6]/b/a').click()
                time.sleep(5)

                # Step 1: Switch to the iframe
                #iframe = driver.find_element(By.XPATH, '//*[@id="divDocumentShowPopUp"]/iframe')  # Adjust the XPath to your iframe element
                #driver.switch_to.frame(iframe)

                # Step 2: Get the 'src' attribute of the iframe
                iframe_src = driver.find_element(By.XPATH, '//*[@id="divDocumentShowPopUp"]/iframe').get_attribute("src")
                print("Iframe src URL:", iframe_src)
                close_button = driver.find_element(By.XPATH, "//button[@data-dismiss='modal']")
                close_button.click()
                # Step 3: Download the PDF from the iframe's 'src' URL (using requests)
                # If the iframe src is a direct link to a PDF, we can download it via the requests library.//*[@id="divDocumentShowPopUp"]/iframe
                pdf_url = iframe_src  # Assuming the src points directly to a PDF file

                # Sending a GET request to fetch the PDF
                response = requests.get(pdf_url)
                filesname = reg_no + '-certificate.pdf'
                # Save the PDF to a file
                if response.status_code == 200:
                    with open(filesname, "wb") as file:
                        file.write(response.content)
                    print("PDF downloaded successfully.")
                else:
                    print("Failed to download the PDF.")

                # Wait for the download to start (adjust time as needed)
                
                
            except:
                pass
            '''
            link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="gridview"]/div[1]/div/table/tbody/tr/td[5]/b/a'))
            )
            link.click()
             
            time.sleep(10)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(3) 
             
             
             
            try:
                project_details['Do you have any Past Experience ?'] = driver.find_element(By.XPATH, '//div[contains(@class, "form-group")]//label[@for="Do_you_have_any_Past_Experience__"]/ancestor::div[@class="form-group"]/div[2]').text
                 
            except:
                pass
             
            try:
                
 
                # Step 2: Locate the row containing the District label and value after the header
                 
                
                project_details['district'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyDistrictValue"]/ancestor::div[contains(@class, "form-group")]/div[2]')
                project_details['street'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyStreet"]/ancestor::div[contains(@class, "form-group")]/div[2]')
                project_details['locality'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyLocality"]/ancestor::div[contains(@class, "form-group")]/div[4]')
                project_details['state'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyState"]/ancestor::div[contains(@class, "form-group")]/div[4]')
                project_details['mandal'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyTalukaValue"]/ancestor::div[contains(@class, "form-group")]/div[4]')
                
                project_details['Village/City/Town'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyVillageValue"]/ancestor::div[contains(@class, "form-group")]/div[2]')
                project_details['Proposed Date of Completion'] = getText('//*[@id="DivProject"]/div[1]/div[2]/div[4]/div/div[2]')

                project_details['Revised_Proposed Date of Completion'] = getText('//div[contains(@class, "form-group")]//label[text()="Revised Proposed Date of Completion"]/following::div[contains(@class, "col-md-3")][1]')
                

               
                 
            except:
                pass
            
            try:
                labels = driver.find_elements(By.XPATH, "//div[@class='form-group']//label")

                # Define the labels you want to extract
                target_labels = [
                    "Pin Code",
                    "Project Type",
                    "Total Area(In sqmts)",
                    "Total Building Units (as per approved plan)"
                    ""
                ]

                for label in labels:
                    # Get the label text
                    label_text = label.text
                    #print(f"Found label: {label_text}")  # Print the label for debugging
                    
                    # Check if the label text matches any of the target labels
                    if label_text in target_labels:
                        try:
                            # Print the HTML structure around this label to debug
                            parent = label.find_element(By.XPATH, "./..")  # Get the parent of the label
                            #print("Parent HTML:", parent.get_attribute("outerHTML"))
                            
                            # Adjust the XPath to locate the sibling value div
                            value = None
                            try:
                                # Looking for the next sibling div with the value (after the label's parent div)
                                value = parent.find_element(By.XPATH, "following-sibling::div").text
                            except Exception as e:
                                print(f"Error in finding value for {label_text}: {e}")
                                
                            # If value is not found, let's try looking for a specific sibling `div` or another span
                            if not value:
                                try:
                                    value = parent.find_element(By.XPATH, "following-sibling::div[2]").text
                                except Exception as e:
                                    print(f"Error in finding value for {label_text}: {e}")
                            
                            # If a value is found, print it
                            if value:
                                project_details[label_text] = value
                                #print(f"Label: {label_text}, Value: {value}")
                            else:
                                project_details[label_text] = ""
                                print(f"Value not found for {label_text}")

                        except Exception as e:
                            print(f"Error retrieving value for {label_text}: {str(e)}")
                            
                #project_details['Pin Code'] = getText('//div[contains(@class, "form-group")]//label[@for="PersonalInfoModel_CompanyPinCode"]/ancestor::div[@class="form-group"]/div[2]')
            except:
                
                pass

            try:
                table = driver.find_element(By.XPATH, '//*[@id="DivBuilding"]/div/table')

                with open('building_details.csv', mode='a', newline='', encoding='utf-8') as main_csv_file:
                    main_writer = csv.writer(main_csv_file)

                    if main_csv_file.tell() == 0:
                        main_writer.writerow(["reg_no", "Sr. No.", "Project Name", "Name", "Proposed Date of Completion", "Number of Basement", 
                                            "Number of Plinth", "Number of Podium", "Number of Slab of Super Structure", 
                                            "Number of Stilts", "Number of Open Parking", "Total Parking Area"])

                    rows = table.find_elements(By.XPATH, ".//tbody/tr")
                    for row in rows:
                        columns = row.find_elements(By.XPATH, ".//td")
                        #print('LEN',len(columns))
                        if len(columns) > 0:
                            data = []
                            
                             
                        
                             
                            if len(columns) == 11:
                                for col in columns:
                                    td1 = col.text.strip()
                                    #print('td1',td1)
                                    
                                    data.append(td1)
                                    
                                if data:
                                    data.insert(0, reg_no)
                                    main_writer.writerow(data)
                                else:
                                    continue
                            nested_table_elements = columns[2].find_elements(By.XPATH, ".//table")  
                            for nested_table in nested_table_elements:
                                
                                # Get all header text (cleaning extra spaces)
                                headers = [header.text.strip() for header in nested_table.find_elements(By.XPATH, ".//th")]

                                
                                if "Tasks / Activity" in headers and "Percentage of Work" in headers:
                                    continue  

                                with open('building_details_with_child.csv', mode='a', newline='', encoding='utf-8') as child_csv_file:
                                    child_writer = csv.writer(child_csv_file)

                                    if child_csv_file.tell() == 0:
                                        child_writer.writerow(["reg_no", "Sr. No.", "Floor ID", "Mortgage Area", "Apartment Type", 
                                                            "Saleable Area (in Sqmts)", "Number of Apartment", "Number of Booked Apartment"])

                                    nested_rows = nested_table.find_elements(By.XPATH, ".//tbody/tr")
                                    for nested_row in nested_rows:
                                        nested_columns = nested_row.find_elements(By.XPATH, ".//td")
                                        if len(nested_columns) > 0:
                                            nested_data = [col.text.strip() for col in nested_columns]
                                            nested_data.insert(0, reg_no)
                                            child_writer.writerow(nested_data)

            except Exception as e:
                print("Error:", str(e))












            
            
            '''
            try:
                
                
                rowApproval = driver.find_element(By.XPATH, "//td[span[text()='Proforma of the allotment letter and agreement for sale']]//ancestor::tr")

                # Now locate the "View" button in the same row using following-sibling or descendant.
                view_button = rowApproval.find_element(By.XPATH, ".//button[contains(@title, 'View')]")

                # Click the "View" button
                view_button.click()
                time.sleep(3)
                iframe_src = driver.find_element(By.XPATH, '//*[@id="divDocumentShowPopUp"]/iframe').get_attribute("src")
                print("Iframe src URL:", iframe_src)
                close_button = driver.find_element(By.XPATH, "//button[@data-dismiss='modal']")
                close_button.click()
                # Step 3: Download the PDF from the iframe's 'src' URL (using requests)
                # If the iframe src is a direct link to a PDF, we can download it via the requests library.//*[@id="divDocumentShowPopUp"]/iframe
                pdf_url = iframe_src  # Assuming the src points directly to a PDF file

                # Sending a GET request to fetch the PDF
                response = requests.get(pdf_url)
                filesname = reg_no + '-Proforma of the allotment letter and agreement for sale.pdf'
                # Save the PDF to a file
                if response.status_code == 200:
                    with open(filesname, "wb") as file:
                        file.write(response.content)
                    print("PDF downloaded successfully.")
                else:
                    print("Failed to download the PDF.")
            except:
                pass
            try:
                 
                rowApproval = driver.find_element(By.XPATH, "//td[span[text()='Certificates of Architect (Form 4)']]//ancestor::tr")

                # Now locate the "View" button in the same row using following-sibling or descendant.
                view_button = rowApproval.find_element(By.XPATH, ".//button[contains(@title, 'View')]")

                # Click the "View" button
                view_button.click()
                time.sleep(3)
                iframe_src = driver.find_element(By.XPATH, '//*[@id="divDocumentShowPopUp"]/iframe').get_attribute("src")
                print("Iframe src URL:", iframe_src)
                close_button = driver.find_element(By.XPATH, "//button[@data-dismiss='modal']")
                close_button.click()
                # Step 3: Download the PDF from the iframe's 'src' URL (using requests)
                # If the iframe src is a direct link to a PDF, we can download it via the requests library.//*[@id="divDocumentShowPopUp"]/iframe
                pdf_url = iframe_src  # Assuming the src points directly to a PDF file

                # Sending a GET request to fetch the PDF
                response = requests.get(pdf_url)
                filesname = reg_no + '-Certificates of Architect (Form 4).pdf'
                # Save the PDF to a file
                if response.status_code == 200:
                    with open(filesname, "wb") as file:
                        file.write(response.content)
                    print("PDF downloaded successfully.")
                else:
                    print("Failed to download the PDF.")
            except:
                pass
            try:
                 
                rowApproval = driver.find_element(By.XPATH, "//td[span[text()='Copy of Approval Layout Plan']]//ancestor::tr")

                # Now locate the "View" button in the same row using following-sibling or descendant.
                view_button = rowApproval.find_element(By.XPATH, ".//button[contains(@title, 'View')]")

                # Click the "View" button
                view_button.click()
                time.sleep(3)
                iframe_src = driver.find_element(By.XPATH, '//*[@id="divDocumentShowPopUp"]/iframe').get_attribute("src")
                print("Iframe src URL:", iframe_src)
                close_button = driver.find_element(By.XPATH, "//button[@data-dismiss='modal']")
                close_button.click()
                # Step 3: Download the PDF from the iframe's 'src' URL (using requests)
                # If the iframe src is a direct link to a PDF, we can download it via the requests library.//*[@id="divDocumentShowPopUp"]/iframe
                pdf_url = iframe_src  # Assuming the src points directly to a PDF file

                # Sending a GET request to fetch the PDF
                response = requests.get(pdf_url)
                filesname = reg_no + '-Approval Layout Plan.pdf'
                # Save the PDF to a file
                if response.status_code == 200:
                    with open(filesname, "wb") as file:
                        file.write(response.content)
                    print("PDF downloaded successfully.")
                else:
                    print("Failed to download the PDF.")
            except:
                pass
                '''
        except:
             
            continue
        
         
         
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        #print(project_details) 
        try:
            # Prepare data to be written to CSV
            csv_file = 'telangana_project_details.csv'

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
         
        
                
        
         
        
            

          
              
                   

 
         

