from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
import time
import os
import re  # For sanitizing filenames

# Setup Chrome Options
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
# options.add_argument('--headless')  # Run in headless mode
options.add_argument('start-maximized')
options.add_argument("--log-level=3")

# Initialize WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Open Bihar RERA page
driver.get('https://rera.bihar.gov.in/RegisteredPP.aspx')

# Create directory for QR codes if not exists
if not os.path.exists("QR_Codes"):
    os.makedirs("QR_Codes")

pagenum = 2  # Start page number for pagination

while True:  # Loop through all pages
    for i in range(2, 11):  # Iterate through first 10 project links
        try:
            # Locate the project link dynamically
            project_xpath = f'/html/body/form/div[3]/section/div[2]/div/div/div[2]/div/table/tbody/tr[{i}]/td[1]/a'
            project = wait.until(EC.element_to_be_clickable((By.XPATH, project_xpath)))

            # Get registration number
            regnum = driver.find_element(By.XPATH, f'//*[@id="ContentPlaceHolder1_GV_Building"]/tbody/tr[{i}]/td[2]').text.strip()
            
            # Sanitize filename (remove invalid characters)
            regnum = re.sub(r'[\/:*?"<>|]', '_', regnum)
            if not regnum:
                regnum = f"page{pagenum-1}_project{i}"  # Fallback name

            print(f"Processing: {regnum}")

            # Hover and click the project link
            ActionChains(driver).move_to_element(project).perform()
            project.click()

            # Wait for new window and switch
            wait.until(EC.number_of_windows_to_be(2))
            new_window = [handle for handle in driver.window_handles if handle != driver.current_window_handle][0]
            driver.switch_to.window(new_window)

            # Wait for QR code and take a screenshot
            qr_code_elements = driver.find_elements(By.XPATH, '/html/body/form/center/table[1]/tbody/tr/td/fieldset[2]/table[1]/tbody/tr[2]/td[4]/img')
            if qr_code_elements:
                qr_code = qr_code_elements[0]
                qr_code.screenshot(f'QR_Codes/qrcode_{regnum}.png')
                print(f"QR code saved: QR_Codes/qrcode_{regnum}.png")
            else:
                print(f"QR code not found for {regnum}")

            # Close the current tab and switch back
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print(f"Error processing page {pagenum - 1}, project {i}: {e}")

    # Find and click the "Next" page button
    try:
        next_button = driver.find_element(By.XPATH, f"//a[contains(@href, 'Page${pagenum}')]")
        if next_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Wait for next page to load
            pagenum += 1  # Increment page count
        else:
            print("Next button is disabled, stopping pagination.")
            break
    except Exception:
        print("No more pages available or error in finding the next button.")
        break
# Close the browser
driver.quit()
