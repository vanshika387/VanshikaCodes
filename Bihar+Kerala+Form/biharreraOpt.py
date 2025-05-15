import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# URL of the website
url = "https://rera.bihar.gov.in/RegisteredPP.aspx"

# CSV file path
csv_file_path = 'c:/Users/vanshika.alang/Desktop/Training/biharrera_data.csv'

# Read existing registration IDs from the CSV file
existing_ids = set()
if os.path.exists(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            if row:
                existing_ids.add(row[0])  # Assuming Registration ID is the first column

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)
time.sleep(2)  # Wait for the page to load

# Extract table headers
soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
headers = [header.text.strip() for header in table.find_all('th')]

# Extract table rows
new_rows = []
pagenum = 1

while True:
    # Extract the current page's rows
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
    
    for row in table.find_all('tr')[1:-2]:  # Skip the header row and last extra rows
        cells = row.find_all('td')
        row_data = [cell.text.strip() for cell in cells]
        if row_data:
            registration_id = row_data[0]  # Assuming Registration ID is in the first column
            if registration_id not in existing_ids:
                new_rows.append(row_data)
                existing_ids.add(registration_id)  # Add to existing set to avoid duplicates
    
    print(f"Page {pagenum} checked")
    pagenum += 1
    time.sleep(2)
    
    # Find and click the next page button
    try:
        next_button = driver.find_element(By.XPATH, f"//a[contains(@href, 'Page${pagenum}')]")
        if next_button.is_enabled():
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Wait for the next page to load
        else:
            print("Next button is disabled")
            break
    except Exception:
        print("No more pages or error in finding next button.")
        break

# Close the WebDriver
driver.quit()

# Append new data to CSV if any new rows found
if new_rows:
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(new_rows)
    print(f"{len(new_rows)} new records appended to {csv_file_path}")
else:
    print("No new records found.")
