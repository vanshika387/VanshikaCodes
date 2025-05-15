import pandas as pd
import ast
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm

# Load input
df = pd.read_excel(r"C:\housing\noida\error 140.xlsx")
df_valid = df[pd.notna(df['url'])]

# Chrome setup
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 5)

# Results
all_data = []

for _, row in tqdm(df_valid.iterrows(), total=df_valid.shape[0], desc="Scraping projects"):
    project_id = row['xid']
    url = row['url']
    print(f"\nProcessing: {project_id}, URL: {url}")

    try:
        driver.get(url)
        driver.implicitly_wait(5)

        try:
            popup = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[2]/div[2]/div[1]/div[1]/div/button")))
            popup.click()
        except: pass

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
        }

        # Process Amenities
        if data["Amenities - List"] != "Not Found":
            amenities = [i for i in data["Amenities - List"].split("\n") if i.strip().lower() != "less"]
            data["Amenities - List"] = ", ".join(amenities)
            data["Amenities - Count"] = len(amenities)
        else:
            data["Amenities - Count"] = 0

        # Parse overview table
        try:
            raw = data["overview table"]
            items = [i for i in raw.split("\n") if i.strip().lower() != "check rera status"]
            pairs = {items[i]: items[i+1] for i in range(0, len(items)-1, 2)}
        except:
            pairs = {}

        data["Sizes"] = pairs.get("Sizes", None)
        data["Project Area"] = pairs.get("Project Area", None)
        data["Launch Date"] = pairs.get("Launch Date", None)
        data["Project Size - Tower Count"] = pairs.get("Project Size - Tower Count", None)
        data["RERA"] = pairs.get("Rera Id", None)
        data["Possession Starts"] = pairs.get("Possession Starts", None)

        # Extract tower/unit counts from description
        project_size_str = pairs.get("Project Size", "").lower()
        tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', project_size_str)
        unit_match = re.search(r'(\d+)\s*units?', project_size_str)
        data["Project Size - Tower Count"] = tower_match.group(1) if tower_match else None
        data["Project Size - Unit Count"] = unit_match.group(1) if unit_match else None

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

        # Image and Video Count
        data["Photos Count"] = "Not Found"
        data["Videos Count"] = "Not Found"
        try:
            try:
                driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[3]/div[3]/img").click()
            except:
                driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[4]/div[3]/img[2]").click()
            driver.implicitly_wait(5)
            count = driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]").text
            video_tab = driver.find_element(By.XPATH, "/html/body/div/div[5]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]")
            video_tab.click()
            vcount = driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]").text

            total_count = int(count.split("/")[-1])
            img_count = int(count.split("/")[0])
            vid_count = int(vcount.split("/")[0])
            actual_vid = 0 if vid_count == 0 else img_count - vid_count

            data["Photos Count"] = total_count - actual_vid
            data["Videos Count"] = actual_vid
        except:
            data["Photos Count"] = "Not Found"
            data["Videos Count"] = "Not Found"

        all_data.append(data)

    except Exception as ex:
        print(f"Error on {project_id}: {ex}")
        continue

driver.quit()

# Final output
cols = [
    'Project Name', 'Builder Name', 'Project Address', 'Avg Price psft', 'Completion date',
    'Sizes', 'Project Area', 'RERA', 'Project Size - Tower Count', 'Project Size - Unit Count',
    'Configurations', 'Amenities - Count', 'Amenities - List',
    'Photos Count', 'Videos Count', 'Review Count',
    'Builder-Established Date', 'Builder-Project count', 'Builder description',
    'Possession Status', 'Launch Date'
]

df_final = pd.DataFrame(all_data)
df_final = df_final[cols]
df_final.to_excel("final_housing_data_with_media_counts.xlsx", index=False)
print("Saved to final_housing_data_with_media_counts.xlsx")
