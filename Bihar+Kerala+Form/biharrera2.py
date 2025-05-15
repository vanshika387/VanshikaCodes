import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# URL of the website
url = "https://rera.bihar.gov.in/RegisteredPP.aspx"

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)
time.sleep(2)  # Wait for the page to load

# Extract table headers
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
headers = [header.text for header in table.find_all('th')]
print("Headers:", headers)

# Extract table rows
rows = []
pagenum = 1

while True:
    # Extract the current page's rows
    if(pagenum > 183):
        print("No more pages")
        break
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
    for row in table.find_all('tr')[1: -2]:  # Skip the header row
        cells = row.find_all('td')
        row_data = [cell.text.strip() for cell in cells]
        if row_data:
            rows.append(row_data)
    print(f"Page {pagenum}")
    print("Rows:", rows, "\n")
    
    # Find and click the next page button
    # try:
    pagenum += 1
    time.sleep(2)
    # next_button = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_GV_Building"]/tbody/tr[12]/td/table/tbody/tr/td[2]/a')
    page_link = driver.find_element(By.XPATH, f"//a[contains(@href, 'Page${pagenum}')]")        
    # Perform the click action 
    if(pagenum <= 183) :
        driver.execute_script("arguments[0].click();", page_link)
    # if next_button:
    #     print("hello")
    #     time.sleep(2)
    #     next_button.click()
    #     time.sleep(5)  # Wait for the next page to load
    # else:
    #     print("No more pages found")
    print("Next page clicked" , pagenum )
    # pagenum += 1
    time.sleep(2)  # Wait for the next page to load
    # except:
    # if(pagenum > 183):
    #     print("No more pages")
    #     break

# Close the WebDriver
driver.quit()

# Write data to CSV
csv_file_path = 'c:/Users/vanshika.alang/Desktop/Training/biharrera2_data.csv'
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Data has been written to {csv_file_path}")
