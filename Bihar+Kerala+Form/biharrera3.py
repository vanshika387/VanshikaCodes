import requests
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# URL of the website
url = "https://rera.bihar.gov.in/RegisteredPP.aspx"

# Send a GET request to the website
response = requests.get(url)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get(url)


# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table
    table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
    
    # Extract table headers
    headers = [header.text for header in table.find_all('th')]
    print("Headers:", headers)
    
    # Extract table rows
    rows = []
    '''
    try:
        for row in table.find_all('tr')[1: -2]:  # Skip the header row
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]
            rows.append(row_data)
    except Exception as e:
        print(f"Error extracting rows: {e}")
        # Handle pagination using Selenium WebDriver
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
    '''
    pagenum = 1
        
    try:
        while True:
            # Extract the current page's rows
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table', {'id': 'ContentPlaceHolder1_GV_Building'})
            for row in table.find_all('tr')[1: -2]:  # Skip the header row
                cells = row.find_all('td')
                row_data = [cell.text.strip() for cell in cells]
                if row_data:
                    rows.append(row_data)
            print("Rows:", rows)
            
            # Find and click the next page button
            print ("pagenum ", pagenum)
            pagenum += 1
            
            # pagenum += 1
    except Exception as e:
        print(f"Error navigating pages: {e}")
    try: 
        next_button = driver.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_GV_Building"]/tbody/tr[12]/td/table/tbody/tr/td[{pagenum}]/a')
        # if 'disabled' in next_button.get_attribute('class'):
        #     break  # Exit loop if no more pages
        next_button.click()
        print("Next button clicked")
        exit()
    except:
        print("No more pages")
        pass
else:
    print("Failed to retrieve the webpage")

csv_file_path = 'c:/Users/vanshika.alang/Desktop/Training/biharrera_data.csv'

with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Data has been written to {csv_file_path}")
