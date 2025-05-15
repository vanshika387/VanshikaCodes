import pandas as pd
import csv
import ast
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from tqdm import tqdm

def image_vdo_count(driver, xid):
        output_data = []  # Initialize output_data as an empty list
        image_count = "Not Found"  # Initialize image_count to avoid undefined variable error
        video_count = "Not Found"  # Initialize video_count to avoid undefined variable error
        
        try:
    
            # Try extracting image count
            try:
                try:
                    photos = driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[3]/div[3]/img")
                except:
                    photos = driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[4]/div[3]/img[2]")
                photos.click()
                driver.implicitly_wait(5)
                count = driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]")
                image_count = count.text
            except:
                pass
    
            # Try extracting video count
            try:
                video = driver.find_element(By.XPATH, "/html/body/div/div[5]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]")
                if video.text == "Videos":
                    video.click()
                    v = driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]")
                    video_count = v.text
                else:
                    video_count = "0"
            except:
                pass
    
        except:
            print(f"Error processing image, video counts for {xid}")
    
        output_data.append({
            'xid': xid,
            'image_count': image_count,
            'video_count': video_count
        })
    
        time.sleep(1)
    
        # Process counts
        imgvv = pd.DataFrame(output_data)
        img_count_list = []
        vv_count_list = []
        total_count_list = []
        
        for _, row in imgvv.iterrows():
            if row["image_count"] == "Not Found" or row["video_count"] == "Not Found":
                img_count_list.append("Not Found")
                vv_count_list.append("Not Found")
                total_count_list.append("Not Found")
                continue
        
            try:
                total_count = int(row["image_count"].split("/")[-1])
                img_count = int(row["image_count"].split("/")[0])
                vv_count = int(row["video_count"].split("/")[0])
        
                vv = 0 if vv_count == 0 else img_count - vv_count
        
                img_count_list.append(total_count - vv)
                vv_count_list.append(vv)
                total_count_list.append(total_count)
            except:
                img_count_list.append("Parse Error")
                vv_count_list.append("Parse Error")
                total_count_list.append("Parse Error")
        
        # Add final computed columns
        imgvv["Final_Image_Count"] = img_count_list
        imgvv["Final_Video_Count"] = vv_count_list
        imgvv["Total_Media_Count"] = total_count_list
        
        # Drop intermediate columns
        imgvv.drop(columns=["image_count", "video_count"], inplace=True)

        # print(img_count_list, vv_count_list, total_count_list)
        
        return img_count_list[0], vv_count_list[0], total_count_list[0]


# Load input
df = pd.read_csv("individualCrawler/auditUrls.csv")
df_valid = df[pd.notna(df['housing.com link'])]

# Chrome setup
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 5)

# Prepare CSV writer for housing details
housing_output_file = "individualCrawler/final_housing_data.csv"
with open(housing_output_file, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    if( f.tell() == 0):  # Check if file is empty
        # Write header only if the file is empty
        writer.writerow([
            'Project Name', 'Builder Name', 'Project Address', 'Avg Price psft', 'Completion date',
            'Sizes', 'Project Area', 'RERA', 'Project Size - Tower Count', 'Project Size - Unit Count',
            'Configurations', 'Amenities - Count', 'Amenities - List',
            'Photos Count', 'Videos Count', 'Total Count' ,'Review Count',
            'Builder-Established Date', 'Builder-Project count', 'Builder description',
            'Possession Status', 'Launch Date'
        ])

# Prepare CSV writer for floor plan
floorplan_output_file = 'individualCrawler/housingFloorPlanData.csv'
with open(floorplan_output_file, 'a', newline='', encoding='utf-8') as outcsv:
    writer = csv.writer(outcsv)
    if outcsv.tell() == 0:
        writer.writerow(['XID', 'Project Name', 'Configuration', 'List Item', 'Price'])

for _, row in tqdm(df_valid.iterrows(), total=df_valid.shape[0], desc="Scraping projects"):
    project_id = row['XID']
    url = row['housing.com link']
    print(f"\nProcessing: {project_id}, URL: {url}")

    try:
        driver.get(url)
        driver.implicitly_wait(5)

        # Close popup
        # Click the 'Ok, Got it' button if it appears
        try:
            ok_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
            )
            driver.execute_script("arguments[0].click();", ok_button)
            print("Clicked 'Ok, Got it' button.")
        except:
            print("No 'Ok, Got it' button found or already dismissed.")

        time.sleep(5)

        # Click expandable sections
        buttons = [
            "//*[@id='amenities']/div[2]/div[2]/div[3]/h3/div",
            "//*[@id='amenities']/div[2]/div[2]/div[2]/h3/div",
            "//*[@id='amenities']/div[1]/section/div/div[12]/div",
            "//*[@id='aboutDeveloper']/div[1]/div/div[2]/div/span"
        ]
        for b in buttons:
            try: wait.until(EC.element_to_be_clickable((By.XPATH, b))).click()
            except: pass

        def get_text(xpath):
            try: return driver.find_element(By.XPATH, xpath).text.strip()
            except: return "Not Found"

        data = {
            "XID": project_id,
            "Project Name": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1'),
            "Builder Name": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/a/span'),
            "Project Address": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]'),
            "Avg Price psft": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/span[2]'),
            "Completion date": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[2]/div[1]'),
            "Configurations": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[1]/div[1]'),
            "Builder-Established Date": get_text('//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[1]/div[1]'),
            "Builder-Project count": get_text('//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[2]/div[1]'),
            "Builder description": get_text('//*[@id="aboutDeveloper"]/div[1]/div/div[2]/div/div'),
            "overview table": get_text('//*[@id="overviewDetails"]/section/div/table/tbody'),
            "Amenities - List": get_text('//*[@id="amenities"]/div'),
            "Possession Status": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[2]/div[1]')
        }

        if(data["Project Name"] == "Not Found"):
            print(f"Project Name not found for {project_id}. Skipping.")
            continue

        # Process Amenities
        if data["Amenities - List"] != "Not Found":
            amenities = [i for i in data["Amenities - List"].split("\n") if i.strip().lower() != "less"]
            data["Amenities - List"] = ", ".join(amenities)
            data["Amenities - Count"] = len(amenities)
        else:
            data["Amenities - Count"] = 0

        # Overview parsing
        try:
            raw = data["overview table"]
            items = [i for i in raw.split("\n") if i.strip().lower() != "check rera status"]
            pairs = {items[i]: items[i+1] for i in range(0, len(items)-1, 2)}
        except:
            pairs = {}

        data["Sizes"] = pairs.get("Sizes", None)
        data["Project Area"] = pairs.get("Project Area", None)
        data["Launch Date"] = pairs.get("Launch Date", None)
        data["RERA"]= pairs.get("Rera Id", None)
        data["Possession Status"] = pairs.get("Possession Status", None)
        data["Possession Starts"] = pairs.get("Possession Starts", None)

        project_size_str = pairs.get("Project Size", "").lower()
        tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', project_size_str)
        unit_match = re.search(r'(\d+)\s*units?', project_size_str)

        data["Project Size - Tower Count"] = tower_match.group(1) if tower_match else None
        data["Project Size - Unit Count"] = unit_match.group(1) if unit_match else None

        # data["Photos Count"] = 0
        # data["Videos Count"] = 0
        # data["Review Count"] = 0

        # Possession status
        try:
            text1 = driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
            text2 = driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[1]")
            if text1.text == text2.text:
                data["Possession Status"] = driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]").text
        except:
            data["Possession Status"] = "Not Found"

        # Reviews
        data["Review Count"] = 0
        try:
            text3 = driver.find_element(By.XPATH, "//*[@id='reviewBanner']/section/div[1]/div[1]/div/span")
            if text1.text == text3.text:
                review = driver.find_element(By.CSS_SELECTOR, "#reviewBanner h2 span")
                data["Review Count"] = review.text
        except:
            data["Review Count"] = 0

        image_count, video_count, total_count = image_vdo_count(driver, project_id)

        # Write housing data row
        with open(housing_output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data["Project Name"], data["Builder Name"], data["Project Address"], data["Avg Price psft"], data["Completion date"],
                data["Sizes"], data["Project Area"], data["RERA"], data["Project Size - Tower Count"], data["Project Size - Unit Count"],
                data["Configurations"], data["Amenities - Count"], data["Amenities - List"],
                image_count, video_count, total_count, data["Review Count"],
                data["Builder-Established Date"], data["Builder-Project count"], data["Builder description"],
                data["Possession Status"], data["Launch Date"]
            ])

        # ========== FLOOR PLAN SECTION ==========
        try:
            list1 = driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")
            list_items = list1.find_elements(By.TAG_NAME, "li")
            for item in list_items:
                driver.execute_script("arguments[0].click();", item)
                time.sleep(1)
                config_item = item.text.strip()

                previous_data = set()
                while True:
                    try:
                        nested = driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
                        nested_items = nested.find_elements(By.TAG_NAME, "li")
                        current_data = set()
                        for sub in nested_items:
                            list_text = sub.text.strip()
                            current_data.add(list_text)
                            driver.execute_script("arguments[0].click();", sub)
                            time.sleep(1)
                            try:
                                price_element = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
                                price_text = price_element.text.strip()
                            except:
                                price_text = "Price not found"

                            with open(floorplan_output_file, 'a', newline='', encoding='utf-8') as outcsv:
                                writer = csv.writer(outcsv)
                                writer.writerow([project_id, data["Project Name"], config_item, list_text, price_text])

                        if current_data == previous_data:
                            break
                        previous_data = current_data

                        try:
                            next_btn = driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
                            if "css-hskvoc" in next_btn.get_attribute("class"):
                                break
                            driver.execute_script("arguments[0].click();", next_btn)
                            time.sleep(2)
                        except:
                            break
                    except:
                        break
        except Exception as e:
            print(f"Floor plan extraction failed for {project_id}: {e}")

    except Exception as ex:
        print(f"Error on {project_id}: {ex}")
        continue

driver.quit()
print("Scraping complete.")
