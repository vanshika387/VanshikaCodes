import time
import csv
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
 
# Setup Selenium WebDriver
options = Options()
#options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
 
# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
 
# Read input CSV (Skipping first row)
input_file = "Magicbricks_links.csv"
output_file = "magicbricks.csv"
# Read CSV using pandas
df = pd.read_csv(input_file, skiprows=1, header=None)  # Skip first row
xids = df[0].tolist()  # Extract XIDs from the first column
urls = df[3].tolist()  # Extract URLs from the fourth column
 
# Filter URLs that contain 'pdpid' with other text before and after
filtered_urls = []
filtered_xids = []
for xid, url in zip(xids, urls):
    if 'pdpid' in url:
        filtered_urls.append(url)
        filtered_xids.append(xid)
 
urls = filtered_urls
xids = filtered_xids
 
# Work on top 20 records
urls = urls[50:]
xids = xids[50:]
# xids=["1","2"]
# urls=["https://www.magicbricks.com/shriram-solitaire-yelahanka-new-town-bangalore-pdpid-4d4235343036333233","https://www.magicbricks.com/sapnil-residency-bonhooghly-kolkata-pdpid-4d4235303236323239"]
 
# Prepare output data list
data_list = []
 
# Iterate over each URL
for xid, url in zip(xids, urls):
    print(f"Opening URL: {url}")
    driver.get(url)
    time.sleep(3)  # Wait for elements to load
 
    # Extracting data
    try:
        name = driver.find_element(By.CSS_SELECTOR, "div.pdp__name h1").text.strip()
    except:
        name = "N/A"
   
    try:
        builder = driver.find_element(By.CSS_SELECTOR, "div.pdp__developerName").text.replace("By ", "").strip()
    except:
        builder = "N/A"
   
    try:
        address = driver.find_element(By.CSS_SELECTOR, "div.pdp__location").text.strip()
    except:
        address = "N/A"
   
    try:
        price = driver.find_element(By.XPATH, '//*[@id="nav-overview"]/div[2]/div[1]/div[1]/div').text.strip()
        price = price.replace("₹", "Rs").strip()
        print(price)
    except:
        price = "N/A"
   
    try:
        flat_type = driver.find_element(By.CSS_SELECTOR, "div.pdp__bhkposs--data span.pdp__bhkposs--bhk").text.strip()
    except:
        flat_type = "N/A"
 
    # Extracting additional property details
    property_details = {
        "Price/sq.ft": "N/A",
        "Total Units": "N/A",
        "Project Size": "N/A",
        #"Launch Date": "N/A",
        "BHK": "N/A"
    }
 
    try:
        items = driver.find_elements(By.CSS_SELECTOR, "div.pdp__prunitar--item")
        for item in items:
            try:
                label = item.find_element(By.CLASS_NAME, "pdp__prunitar--label").text.strip()
                value = item.find_element(By.CLASS_NAME, "pdp__prunitar--data").text.strip()
                if label in property_details:
                    if(label == "Price/sq.ft"):
                        value = value.replace("₹", "Rs").strip()
                    property_details[label] = value
            except:
                continue  # Skip if elements not found
    except:
        pass  # If no property details found, continue with "N/A"
 
    try:
        super_area_element = driver.find_element(By.CSS_SELECTOR, "div.pdp__florpripln--brief span.text-semibold")
        super_area = super_area_element.text.strip()
    except:
        try:
            super_area_element = driver.find_element(By.CSS_SELECTOR, "span.pdp__prop__card__bhk")
            super_area_text = super_area_element.text.strip()
            super_area = super_area_text.split()[-2] + " " + super_area_text.split()[-1]  # Extract the sq.ft part
        except:
            super_area = "N/A"
 
   
 
    try:
        view_amenities = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View Amenities')]"))
        )
        driver.execute_script("arguments[0].click();", view_amenities)
        time.sleep(3)  # Wait for amenities section to load
    except:
        print("View Amenities' button not found or could not be clicked.")
     
 
    amenities = []
    try:
        amenities_elements = driver.find_elements(By.CSS_SELECTOR, "div.pdp__maproject__amentext")
        amenities = [amenity.text.strip() for amenity in amenities_elements if amenity.text.strip()]
    except:
        pass
 
    try:
        back_button = driver.find_element(By.XPATH, '//*[@id="moredetails"]/div[6]/div[1]/div[1]')
        driver.execute_script("arguments[0].click();", back_button)
        print(" Back button clicked successfully.")
    except:
        print(" Back button not found.")
 
    try:
        all_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "All"))
        )
        driver.execute_script("arguments[0].click();", all_link)
        time.sleep(1)  # Wait for 'All' link to load
       
        print(" Clicked 'All ' link successfully.")
        try:
            floor_plan_elements = driver.find_elements(By.CSS_SELECTOR, "div.pdp__florpripln--bhk")
            floor_plans = []
            floor_plans_1bhk = []
            floor_plans_2bhk = []
            floor_plans_3bhk = []
            floor_plans_4bhk = []
            floor_plans_5bhk=[]
            for element in floor_plan_elements:
                spans = element.find_elements(By.TAG_NAME, "span")
                if len(spans) == 2:
                    sq_ft = spans[0].text.strip()
                    print(sq_ft)
                    if "BHK" in spans[1].text.strip():
                        if "1 BHK" in spans[1].text.strip():
                            floor_plans_1bhk.append(sq_ft)
                        if "2 BHK" in spans[1].text.strip():
                            floor_plans_2bhk.append(sq_ft)
                        if "3 BHK" in spans[1].text.strip():
                            floor_plans_3bhk.append(sq_ft)
                        if "4 BHK" in spans[1].text.strip():
                            floor_plans_4bhk.append(sq_ft)
                        if "5 BHK" in spans[1].text.strip():
                            floor_plans_5bhk.append(sq_ft)
                           
                    floor_plans.append(sq_ft)
                    next=WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="fp-arrow-next"]'))
                    )
                    driver.execute_script("arguments[0].click();", next)
            joined_floor_plans = ", ".join(floor_plans)
            joined_floor_plans_1bhk = ", ".join(floor_plans_1bhk)
            joined_floor_plans_2bhk = ", ".join(floor_plans_2bhk)
            joined_floor_plans_3bhk = ", ".join(floor_plans_3bhk)
            joined_floor_plans_4bhk = ", ".join(floor_plans_4bhk)
            joined_floor_plans_5bhk = ", ".join(floor_plans_5bhk)
 
       
            if(floor_plans==[]):
                super_area_element = driver.find_element(By.CSS_SELECTOR, "span.pdp__prop__card__bhk")
                super_area_text = super_area_element.text.strip()
                print(super_area_text)
                sq_ft = super_area_text.split()[-2] + " " + super_area_text.split()[-1]  # Extract the sq.ft part
                floor_plans.append(sq_ft)
                if "BHK" in super_area_text:
                    if "1 BHK" in super_area_text:
                        floor_plans_1bhk.append(sq_ft)
                    if "2 BHK" in super_area_text:
                        floor_plans_2bhk.append(sq_ft)
                    if "3 BHK" in super_area_text:
                        floor_plans_3bhk.append(sq_ft)
                    if "4 BHK" in super_area_text:
                        floor_plans_4bhk.append(sq_ft)
                    if "5 BHK" in super_area_text:
                        floor_plans_5bhk.append(sq_ft)
                joined_floor_plans = ", ".join(floor_plans)
                joined_floor_plans_1bhk = ", ".join(floor_plans_1bhk)
                joined_floor_plans_2bhk = ", ".join(floor_plans_2bhk)
                joined_floor_plans_3bhk = ", ".join(floor_plans_3bhk)
                joined_floor_plans_4bhk = ", ".join(floor_plans_4bhk)
                joined_floor_plans_5bhk = ", ".join(floor_plans_5bhk)
        except:
            joined_floor_plans = "N/A"
            joined_floor_plans_1bhk = "N/A"
            joined_floor_plans_2bhk = "N/A"
            joined_floor_plans_3bhk = "N/A"
            joined_floor_plans_4bhk = "N/A"
            joined_floor_plans_5bhk = "N/A"
            print("Floor plans not found.")
               
    except:
        print(" 'All BHK' link not found or could not be clicked.")
 
   
    try:
        read_more = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Read More')]"))
        )
        driver.execute_script("arguments[0].click();", read_more)
        time.sleep(2)  # Wait for expanded content to load
        print(" Clicked 'Read More' successfully.")
    except:
        print(" 'Read More' button not found or could not be clicked.")
 
    property_details2 = {
    "Project Type": "N/A",
    "Property Type": "N/A",
    "Status": "N/A",
    "Launch Date": "N/A",
    "Possession Date": "N/A",
    "Total Towers": "N/A",
    }
 
    try:
        table_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        for row in table_rows:
            try:
                key = row.find_element(By.TAG_NAME, "td").text.strip()
                value = row.find_elements(By.TAG_NAME, "td")[1].text.strip()
               
                if "Project Type" in key:
                    property_details2["Project Type"] = value
                elif "Property Types" in key:
                    property_details2["Property Type"] = value
                elif "Status" in key:
                    property_details2["Status"] = value
                elif "Launch Date" in key:
                    property_details2["Launch Date"] = value
                elif "Possession Date" in key:
                    property_details2["Possession Date"] = value
                elif "Towers" in key:
                    property_details2["Total Towers"] = value
            except:
                continue
    except:
        print(" Table data not found.")
 
   
    # Click Back Button After "Read More"
    try:
        back_button = driver.find_element(By.XPATH, "//*[@id='moredetails']/div[3]/div[1]/div[1]")
        driver.execute_script("arguments[0].click();", back_button)
       
        print(" Back button clicked successfully.")
    except:
        print(" Back button not found.")
 
    # Append data to list
    data_list.append([
        xid, url, name, builder, address, price, flat_type,
        property_details["Price/sq.ft"], property_details["Total Units"],
        property_details["Project Size"],  property_details["BHK"],", ".join(amenities),property_details2["Project Type"],property_details2["Property Type"],property_details2["Status"],property_details2["Launch Date"],property_details2["Possession Date"],property_details2["Total Towers"],joined_floor_plans,joined_floor_plans_1bhk,joined_floor_plans_2bhk,joined_floor_plans_3bhk,joined_floor_plans_4bhk,joined_floor_plans_5bhk
    ])
 
# Close the driver
#driver.quit()
 
# Save to CSV
with open(output_file, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if f.tell() == 0:  # Check if file is empty to write header
        writer.writerow([
            "XID", "URL", "Name", "Builder", "Address", "Price", "Flat Type",
            "Price per Sq.Ft", "Total Units", "Project Size",
            "BHK", "Amenities", "Project Type", "Property Type", "Status", "Launch Date", "Possession Date", "Total Towers", "All floor plans", "1 BHK Floor Plan", "2 BHK Floor Plan", "3 BHK Floor Plan", "4 BHK Floor Plan", "5 BHK Floor Plan"
        ])
    writer.writerows(data_list)

print(f" Data extraction complete. Results appended in {output_file}")

driver.quit()
 
 