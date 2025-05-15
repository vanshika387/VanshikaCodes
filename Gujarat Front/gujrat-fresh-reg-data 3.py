from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl, requests
from openpyxl.workbook import Workbook
import csv
import pdb
from io import BytesIO
from datetime import date
driver = webdriver.Chrome()

driver.get("https://gujrera.gujarat.gov.in/#/")
driver.maximize_window()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
time.sleep(2)
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-home/div[2]/div[6]/div/div/div/div[1]/button').click()
driver.find_element(By.XPATH, '//*[@id="DataFromJson"]/div[1]/div/p[1]/a').click()
time.sleep(10)

def myfunction():
        try:    
                ids = driver.find_element(By.XPATH, '/html/body/app-root/div[1]/div/div/div/app-project-registered-listing/div[3]/div/table/tbody/tr[1]/td[1]').text
                print(ids)
                if 'Loading' in ids:
                    time.sleep(25)
                    myfunction()
                else:
                    return True
        except:
                try: 
                    element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//*[@id='innerHome']/app-project-registered-listing/div[5]/app-loader/div"))
                            )
                    
                    # If the element is found, call the function
                    myfunction()
                except:
                    return True
                        
for x in range(3, 4):
    xpath = '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr['+str(x)+']/td[11]/u/a'

    if(x == 3):
        for i in range(2, 11):
            time.sleep(10)
            driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr[3]/td['+ str(i)+ ']/u/a').click()

            time.sleep(20)
     
            cnt = 0
            cc="NO"
            c=0
            if myfunction() == True:
                pass
            
            table_data = []
            time.sleep(10)
            #driver.find_element(BY.XPATH, '//*[@id="example_length"]/label/select/option[4]').click()
            while True:
                
                # Step 6: Locate the table and extract rows
                table = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                )
                rows = table.find_elements(By.TAG_NAME, 'tr')

                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    if columns:
                        row_data = [col.text for col in columns[:-2]]  # Exclude last two columns
                        table_data.append(row_data)
                
                
                # Step 8: Try to locate and click the "Next" button
                try:
                    # Adjust the XPath/Selector for the pagination button as needed
                    if(i != 9): 
                        next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[10]/a')  # Modify based on your webpage

                    if( i == 9):
                        next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[6]/a')  # Modify based on your webpage

                    # Check if the "Next" button has the 'disabled' class or 'aria-disabled="true"'
                    disabled_class = 'disabled'  # The class that indicates the button is disabled (adjust if needed)
                    aria_disabled = 'true'  # The attribute value indicating the button is disabled

                    # Check if the button has the "disabled" class or is aria-disabled
                    if disabled_class in next_button.get_attribute('class') or next_button.get_attribute('aria-disabled') == aria_disabled:
                        print("Pagination has ended or no more pages.")
                        break

                    # If the "Next" button is not disabled, click it and proceed to the next page
                    next_button.click()

                    # Wait for the table to load after clicking "Next"
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'table'))
                    )
                    time.sleep(1)  # Adjust as necessary
                except Exception as e:
                    # If there's an issue (e.g., no "Next" button), break the loop
                    print("Error or no more pages in mixed:", e)
                    break
            driver.back()
    else :  
        time.sleep(10)
        driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr['+str(x)+']/td[11]/u/a').click()
        
        time.sleep(20)
        
        cnt = 0
        cc="NO"
        c=0
        if myfunction() == True:
            pass
        
        table_data = []
        time.sleep(10)
        #driver.find_element(BY.XPATH, '//*[@id="example_length"]/label/select/option[4]').click()
        while True:
            
            # Step 6: Locate the table and extract rows
            table = driver.find_element(By.TAG_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')

            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                if columns:
                    row_data = [col.text for col in columns[:-2]]  # Exclude last two columns
                    table_data.append(row_data)
            
            
            try:
                # Adjust the XPath/Selector for the pagination button as needed
                next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[10]/a')  # Modify based on your webpage

                # Check if the "Next" button has the 'disabled' class or 'aria-disabled="true"'
                disabled_class = 'disabled'  # The class that indicates the button is disabled (adjust if needed)
                aria_disabled = 'true'  # The attribute value indicating the button is disabled

                # Check if the button has the "disabled" class or is aria-disabled
                if disabled_class in next_button.get_attribute('class') or next_button.get_attribute('aria-disabled') == aria_disabled:
                    print("Pagination has ended or no more pages.")
                    break

                # If the "Next" button is not disabled, click it and proceed to the next page
                next_button.click()

                # Wait for the table to load after clicking "Next"
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                )
                time.sleep(1)  # Adjust as necessary
            except Exception as e:
                # If there's an issue (e.g., no "Next" button), break the loop
                print("Error or no more pages:", e)
                break
        # Step 8: Close the WebDriver
        #driver.quit()
    
    df = pd.DataFrame(table_data)
    df.columns = ['Sr.No.','Project Name','Promoter Name','Promoter Address','Project Type','Email Id','Mobile No','Project Registration No.','District','Approved on'] 
    df.to_csv('gujrat-project-all-front-data-'+str(x)+'.csv', index=False)
    if(x != 3):
        driver.back()
