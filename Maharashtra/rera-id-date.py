from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import PyPDF2
import io
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
import time
import pyautogui
from PIL import ImageGrab, Image 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
import pytesseract, csv
import pandas as pd
from datetime import date

#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\abhishek.a3\AppData\Local\Programs\Tesseract-OCR\tesseract.exe' 
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\vanshika.alang\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
# Initialize Selenium WebDriver (assuming Chrome)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to the webpage
driver.get("https://maharera.maharashtra.gov.in/projects-search-result")
driver.maximize_window()
time.sleep(12)

ids_group = []

cnt = 0

cc="NO"
with open("maharera-focus-date.csv","r") as csvfile:
    records  = csv.reader(csvfile)
    next(records)
    #pdb.set_trace()
    for row in records:
        
        id = row[0]
        xid = row[0]
        
        print(id) 
        driver.find_element(By.ID,'edit-project-name').send_keys(Keys.CONTROL,'a')
        driver.find_element(By.ID,'edit-project-name').send_keys(xid)
        time.sleep(3)
        try:
            actions = ActionChains(driver) 
            actions.send_keys(Keys.ENTER)
            actions.perform()
        except:
            driver.find_element(By.ID,'edit-submit--2').click()
            
        time.sleep(10)
        try:
            if(driver.find_element(By.XPATH,'//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]').text =='No Records Found' or driver.find_element(By.XPATH,'//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]').text == 'Project registration is kept in abeyance by order of Authority'):
                
                continue
            else:
                pass
        except:
            pass
        try:
            # Find and click the link/button to open the PDF popup
            time.sleep(3)
            # driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "smooth"});')
            reg = driver.find_element(By.XPATH,'//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[1]/p[1]').text
            print(reg)

            # element = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[2]/div[1]/div[3]/a')
            # driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            # driver.execute_script("arguments[0].click();", element)

            # Scroll to the portion of the webpage where the registration number is found
            # element = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[1]/p[1]')
            # driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
            try:
                element = driver.find_element(By.CSS_SELECTOR, '#content > div > div.row > div.col-md-9.fullShow.col-lg-12 > div.container > div.row.shadow.p-3.mb-5.bg-body.rounded > div.col-xl-6 > div:nth-child(1) > div:nth-child(3) > a')
                driver.execute_script("arguments[0].click();", element)

            except:
                element = driver.find_element(By.XPATH,'//*[@id="content"]/div/div[2]/div[2]/div[4]/div[2]/div[2]/div[1]/div[3]/a')
                driver.execute_script("arguments[0].click();", element)

            #driver.find_element(By.XPATH,'/html/body').send_keys(Keys.CONTROL + Keys.HOME)
            print('eee')
            time.sleep(10)
            #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.find_element(By.CSS_SELECTOR, '#exampleModal').send_keys(Keys.END)
            #driver.execute_script('arguments[0].scrollIntoView({block: "center", behavior: "smooth"});', followers[-1])
            #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            #driver.find_element(By.ID, "fit").click()
            N = 2  # number of times you want to press TAB

            actions = ActionChains(driver) 
            for _ in range(N):
                actions = actions.send_keys(Keys.TAB)
            actions.perform()
            image_path = "image1.png"
            time.sleep(10)
            driver.save_screenshot(image_path)

            img = Image.open(image_path)

            # Use pytesseract to do OCR on the image
            example_string = pytesseract.image_to_string(img)

            # Print the extracted text
            print("example string", example_string)
            reg_number = "registration number :"
            parts = example_string.split(reg_number)
            if len(parts) > 1:
                 
                after_text = parts[1]
                register_no = after_text.split()[0] 
                print("Text after:", after_text.split()[0])
            else:
                print("not found.")
                register_no = ''
                
            substring = "commencing from"

            # Find the index of the substring
            parts = example_string.split(substring)
            if len(parts) > 1:
                 
                after_text = parts[1]
                commencing_date = after_text.split()[0] 
                print("Text after:", after_text.split()[0])
            else:
                print("not found.")
                commencing_date = ''
 
            #driver.find_element(By.XPATH, '/html/body/div[4]/div[11]/div/button').click()
            driver.find_element(By.CLASS_NAME, "btn-close").click()
            temp_data={'register no': reg, 'commencing from': commencing_date}

            print(temp_data)
             
            ids_group.append(temp_data)

            time.sleep(3)
        except Exception as e:

            print(e)

            cc="YES"

            break
          
 
print(ids_group)   

# Save the data to a CSV file using with open
with open('maharera-reg-commen-date-1.csv', 'a', newline='') as csvfile:
    fieldnames = ['register no', 'commencing from']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Check if the file is empty
    csvfile.seek(0, 2)  # Move the cursor to the end of the file
    if csvfile.tell() == 0:
        writer.writeheader()
        
    for data in ids_group:
        writer.writerow(data)
