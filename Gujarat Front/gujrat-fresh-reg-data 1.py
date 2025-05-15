from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
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
driver.find_element(By.XPATH, '//*[@id="innerHome"]/app-project-registered-count/div/div/div/div[2]/div/table/tbody/tr[5]/td[11]/u/span/a').click()
time.sleep(20)
 
cnt = 0
cc="NO"
c=0
def myfunction():

    ids = driver.find_element(By.XPATH, '/html/body/app-root/div[1]/div/div/div/app-project-registered-listing/div[3]/div/table/tbody/tr[1]/td[1]').text
    print(ids)
    if 'Loading' in ids:
        time.sleep(5)
        myfunction()
    else:
        return True
if myfunction() == True:
    pass
print('YES')
table_data = [] 

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

    # Step 8: Try to locate and click the "Next" button
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
df.to_csv('gujrat-project-all-front-data.csv', index=False)

