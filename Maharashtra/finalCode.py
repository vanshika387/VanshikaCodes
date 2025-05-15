import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import pytesseract, csv
from PIL import Image

# Set up Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\vanshika.alang\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Initialize Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://maharera.maharashtra.gov.in/projects-search-result")
driver.maximize_window()
time.sleep(12)

ids_group = []

with open("maharera-focus-date.csv", "r") as csvfile:
    records = csv.reader(csvfile)
    next(records, None)  # Skip header
    
    for row in records:
        if not row or len(row) < 1:  # Skip empty rows
            continue
        
        xid = row[0].strip()
        print(xid)
        
        search_box = driver.find_element(By.ID, 'edit-project-name')
        search_box.send_keys(Keys.CONTROL, 'a')
        search_box.send_keys(xid)
        time.sleep(3)
        
        try:
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
        except:
            driver.find_element(By.ID, 'edit-submit--2').click()
        
        time.sleep(10)
        
        try:
            result_text = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]').text
            if result_text in ['No Records Found', 'Project registration is kept in abeyance by order of Authority']:
                continue
        except:
            pass
        
        attempt = 0
        while attempt < 3:
            try:
                reg = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[1]/p[1]').text
                print(reg)
                
                try:
                    element = driver.find_element(By.CSS_SELECTOR, '#content div.col-xl-6 div:nth-child(1) div:nth-child(3) > a')
                except:
                    element = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[2]/div[1]/div[3]/a')
                driver.execute_script("arguments[0].click();", element)
                
                time.sleep(10)
                driver.find_element(By.CSS_SELECTOR, '#exampleModal').send_keys(Keys.END)
                
                actions = ActionChains(driver)
                for _ in range(2):
                    actions.send_keys(Keys.TAB)
                actions.perform()
                
                image_path = "image1.png"
                time.sleep(5)
                driver.save_screenshot(image_path)
                img = Image.open(image_path)
                
                extracted_text = pytesseract.image_to_string(img)
                print("Extracted text:", extracted_text)
                
                reg_number = "registration number :"
                parts = extracted_text.split(reg_number)
                register_no = parts[1].split()[0] if len(parts) > 1 else ''
                print("Register No:", register_no)
                
                commencing_date = ''
                substring = "commencing from"
                parts = extracted_text.split(substring)
                if len(parts) > 1:
                    after_text = parts[1].split()
                    commencing_date = after_text[0] if after_text else ''
                print("Commencing Date:", commencing_date)
                
                driver.find_element(By.CLASS_NAME, "btn-close").click()
                ids_group.append({'register no': reg, 'commencing from': commencing_date})
                time.sleep(3)
                break
            
            except Exception as e:
                print(f"Error encountered, retrying... Attempt {attempt + 1}")
                attempt += 1
                if attempt == 10:
                    print("Max retries reached, skipping this record.")
                    break
                driver.refresh()
                time.sleep(10)

# Save the data to a CSV file
output_file = 'finalData.csv'
write_header = not os.path.exists(output_file) or os.stat(output_file).st_size == 0

with open(output_file, 'a', newline='') as csvfile:
    fieldnames = ['register no', 'commencing from']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    if write_header:
        writer.writeheader()
    
    writer.writerows(ids_group)
