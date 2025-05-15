from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            myfunction()
        except:
            return True

def write_to_csv(data, filename):
    header = ['Sr.No.', 'Project Name', 'Promoter Name', 'Promoter Address', 'Project Type', 'Email Id', 'Mobile No', 'Project Registration No.', 'District', 'Approved on']
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Write the header row
        writer.writerows(data)   # Write the actual data

for x in range(3, 4):
    xpath = '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr['+str(x)+']/td[11]/u/a'
    
    if(x == 3):
        for i in range(2, 11):
            time.sleep(10)
            driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr[3]/td['+ str(i)+ ']/u/a').click()
            time.sleep(20)
            
            if myfunction() == True:
                pass
            
            table_data = []
            time.sleep(10)
            
            while True:
                table = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                )
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                for row in rows:
                    columns = row.find_elements(By.TAG_NAME, 'td')
                    if columns:
                        row_data = [col.text for col in columns[:-2]]
                        table_data.append(row_data)
                
                try:
                    if(i != 9): 
                        next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[10]/a')
                    if(i == 9):
                        next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[6]/a')
                    
                    disabled_class = 'disabled'
                    aria_disabled = 'true'
                    
                    if disabled_class in next_button.get_attribute('class') or next_button.get_attribute('aria-disabled') == aria_disabled:
                        print("Pagination has ended or no more pages.")
                        break
                    
                    next_button.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'table'))
                    )
                    time.sleep(1)
                except Exception as e:
                    print("Error or no more pages in mixed:", e)
                    break
            
            write_to_csv(table_data, f'gujrat-project-all-front-data-{x}.csv')
            driver.back()
    else:
        time.sleep(10)
        driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr['+str(x)+']/td[11]/u/a').click()
        time.sleep(20)
        
        if myfunction() == True:
            pass
        
        table_data = []
        time.sleep(10)
        
        while True:
            table = driver.find_element(By.TAG_NAME, 'table')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, 'td')
                if columns:
                    row_data = [col.text for col in columns[:-2]]
                    table_data.append(row_data)
            
            try:
                next_button = driver.find_element(By.XPATH, '//*[@id="foo1"]/pagination-template/ul/li[10]/a')
                
                disabled_class = 'disabled'
                aria_disabled = 'true'
                
                if disabled_class in next_button.get_attribute('class') or next_button.get_attribute('aria-disabled') == aria_disabled:
                    print("Pagination has ended or no more pages.")
                    break
                
                next_button.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'table'))
                )
                time.sleep(1)
            except Exception as e:
                print("Error or no more pages:", e)
                break
        
        write_to_csv(table_data, f'gujrat-project-all-front-data-{x}.csv')
        driver.back()
