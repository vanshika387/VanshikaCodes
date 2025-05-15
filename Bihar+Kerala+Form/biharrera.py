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
    pagenum += 1
    time.sleep(2)
    try:
        next_button = driver.find_element(By.XPATH, f"//a[contains(@href, 'Page${pagenum}')]")
        if next_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Wait for the next page to load
        else:
            print("Next button is disabled")
            break
    except Exception as e:
        print(f"Error clicking next button: {e}")
        break

# Close the WebDriver
driver.quit()

# Write data to CSV
csv_file_path = 'c:/Users/vanshika.alang/Desktop/Training/biharrera_data2.csv'
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Data has been written to {csv_file_path}")