from asyncio import wait
import csv
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from abc import ABC, abstractmethod
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager
import re
import time


class BaseCrawler(ABC):
    def __init__(self):
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)

    @abstractmethod
    def extract_project_data(self, xid: str, url: str, requested_fields: list):
        pass

    def quit(self):
        self.driver.quit()


class MagicBricksCrawler(BaseCrawler):
    def extract_project_data(self, xid, url, requested_fields):
        if not url:
            return None, None
            
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        if not 'pdpid' in url:
            return None, None

        all_data = {
            "XID": xid,
            "URL": url,
            "Project Name": "N/A",
            "Builder Name": "N/A",
            "Location": "N/A",
            "Price Range": "N/A",
            "Price psft": "N/A",
            "Property Type": "N/A",
            "Possesion Date": "N/A",
            "LandMarks": "N/A",
            "Project Size": "N/A",
            "Size Range": "N/A",
            "Launch Date": "N/A",
            "RERA Number": "N/A",
            "Tower Count": "N/A",
            "Unit Count": "N/A",
            "USP": "N/A",
            "BHK": "N/A",
            "Amenity Count": "N/A",
            "Amenities": "N/A",
            "Image Count": "N/A",
            "Specifications": "N/A",
            "Review Count": "N/A",
            "Builder Experience": "N/A",
            "Builder Total Projects": "N/A",
            "Builder Ready to Move Projects": "N/A",
            "Builder Ongoing Projects": "N/A",
            "Builder Info": "N/A",
            "Project Status": "N/A",
            "Video Count": "N/A"
        }
        
        floor_plans = []
        
        print(f"Opening URL: {url} for XID: {xid}")
        self.driver.get(url)
        time.sleep(3)

        # Only extract requested fields
        if "Project Name" in requested_fields:
            try:
                all_data["Project Name"] = self.driver.find_element(By.CSS_SELECTOR, ".pdp__name h1").text.strip()
            except:
                pass

        if "Image Count" in requested_fields:
            try:
                all_data["Image Count"] = self.driver.find_element(By.CSS_SELECTOR, ".pdp__imgcount").get_attribute("textContent").strip()
            except:
                pass

        if "Builder Name" in requested_fields:
            try:
                all_data["Builder Name"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__developerName").text.replace("By ", "").strip()
            except:
                pass

        if any(field in requested_fields for field in ["Builder Total Projects", "Builder Ready to Move Projects", "Builder Ongoing Projects"]):
            try:
                developer_link_element = self.driver.find_element(By.CSS_SELECTOR, "div.about-developer__builder__heading a")
                developer_link = developer_link_element.get_attribute("href")
                
                if developer_link:
                    self.driver.execute_script("arguments[0].click();", developer_link_element)
                    time.sleep(3)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    
                    if "Builder Total Projects" in requested_fields:
                        try:
                            all_data["Builder Total Projects"] = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Total Projects')]/following-sibling::div").text.strip()
                        except:
                            pass
                    
                    if "Builder Ready to Move Projects" in requested_fields:
                        try:
                            all_data["Builder Ready to Move Projects"] = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Projects Completed')]/following-sibling::div").text.strip()
                        except:
                            pass
                    
                    if "Builder Ongoing Projects" in requested_fields:
                        try:
                            all_data["Builder Ongoing Projects"] = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Projects Ongoing')]/following-sibling::div").text.strip()
                        except:
                            pass
                    
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass

        if "Location" in requested_fields:
            try:
                all_data["Location"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__location").text.strip()
            except:
                pass

        if "Price Range" in requested_fields:
            try:
                all_data["Price Range"] = self.driver.find_element(By.XPATH, '//*[@id="nav-overview"]/div[2]/div[1]/div[1]/div').text.strip().replace("₹", "Rs")
            except:
                pass

        if "BHK" in requested_fields:
            try:
                all_data["BHK"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__bhkposs--data span.pdp__bhkposs--bhk").text.strip()
            except:
                pass

        if "Price psft" in requested_fields:
            try:
                items = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__prunitar--item")
                for item in items:
                    try:
                        label = item.find_element(By.CLASS_NAME, "pdp__prunitar--label").text.strip()
                        if label == "Price/sq.ft":
                            all_data["Price psft"] = item.find_element(By.CLASS_NAME, "pdp__prunitar--data").text.strip().replace("₹", "Rs")
                            break
                    except:
                        continue
            except:
                pass

        if "Property Type" in requested_fields or "Possesion Date" in requested_fields or "Launch Date" in requested_fields or "Tower Count" in requested_fields or "Project Status" in requested_fields:
            try:
                table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
                for row in table_rows:
                    try:
                        key = row.find_element(By.TAG_NAME, "td").text.strip()
                        value = row.find_elements(By.TAG_NAME, "td")[1].text.strip()
                        
                        if "Property Types" in key and "Property Type" in requested_fields:
                            all_data["Property Type"] = value
                        elif "Possession Date" in key and "Possesion Date" in requested_fields:
                            all_data["Possesion Date"] = value
                        elif "Launch Date" in key and "Launch Date" in requested_fields:
                            all_data["Launch Date"] = value
                        elif "Towers" in key and "Tower Count" in requested_fields:
                            all_data["Tower Count"] = value
                        elif "Status" in key and "Project Status" in requested_fields:
                            all_data["Project Status"] = value
                    except:
                        continue
            except:
                pass

        if "Project Size" in requested_fields:
            try:
                all_data["Project Size"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Project Size')]/following-sibling::td").text.strip()
            except:
                pass

        if "Unit Count" in requested_fields:
            try:
                all_data["Unit Count"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Total Units')]/following-sibling::td").text.strip()
            except:
                pass

        if "Size Range" in requested_fields:
            try:
                all_data["Size Range"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__florpripln--brief span.text-semibold").text.strip()
            except:
                try:
                    super_area_element = self.driver.find_element(By.CSS_SELECTOR, "span.pdp__prop__card__bhk")
                    super_area_text = super_area_element.text.strip()
                    all_data["Size Range"] = super_area_text.split()[-2] + " " + super_area_text.split()[-1]
                except:
                    pass

        if "Amenities" in requested_fields or "Amenity Count" in requested_fields:
            try:
                view_amenities = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View Amenities')]"))
                )
                self.driver.execute_script("arguments[0].click();", view_amenities)
                time.sleep(3)
                
                amenities_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__maproject__amentext")
                amenities = [amenity.text.strip() for amenity in amenities_elements if amenity.text.strip()]
                
                if "Amenities" in requested_fields:
                    all_data["Amenities"] = ", ".join(amenities)
                if "Amenity Count" in requested_fields:
                    all_data["Amenity Count"] = len(amenities)
                    
                back_button = self.driver.find_element(By.XPATH, '//*[@id="moredetails"]/div[6]/div[1]/div[1]')
                self.driver.execute_script("arguments[0].click();", back_button)
            except:
                pass

        if "USP" in requested_fields:
            try:
                usp_header = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Why Buy in')]"))
                )
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Why Buy in')]"))
                usp_section = usp_header.find_element(By.XPATH, "./following-sibling::div")
                usp_elements = usp_section.find_elements(By.TAG_NAME, "li")
                usps = [li.text.strip() for li in usp_elements if li.text.strip()]
                all_data["USP"] = " | ".join(usps)
            except:
                pass

        if "Specifications" in requested_fields:
            try:
                spec_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pdp__maproject__spaecdd')]/div[contains(@class, 'pdp__maproject__spaceContent')]"))
                )
                specifications = []
                
                try:
                    all_ul_elements = spec_section.find_elements(By.XPATH, ".//ul")
                    for ul in all_ul_elements:
                        parent_text = ul.find_element(By.XPATH, "./preceding-sibling::text()").strip() if ul.find_elements(By.XPATH, "./preceding-sibling::text()") else ""
                        li_elements = ul.find_elements(By.TAG_NAME, "li")
                        
                        if li_elements:
                            section_title = parent_text 
                            if section_title:
                                extracted_text = [f"{section_title}: {li.text.strip()}" for li in li_elements if li.text.strip()]
                            else:
                                extracted_text = [li.text.strip() for li in li_elements if li.text.strip()]
                            specifications.extend(extracted_text)
                except Exception as e:
                    pass

                if not specifications:
                    try:
                        ul_element = spec_section.find_element(By.TAG_NAME, "ul")
                        raw_text = ul_element.get_attribute("innerHTML")
                        if "<br>" in raw_text:
                            extracted_text = [line.strip() for line in raw_text.split("<br>") if line.strip()]
                            specifications.extend(extracted_text)
                    except:
                        pass

                all_data["Specifications"] = "\n".join(specifications) if specifications else "N/A"
            except:
                pass

        if "Builder Info" in requested_fields:
            try:
                read_more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "readmore")))
                self.driver.execute_script("arguments[0].click();", read_more_button)
                time.sleep(2)
                
                all_data["Builder Info"] = self.driver.find_element(By.CSS_SELECTOR, "div.popup__body.aboutdeveloper").text.strip()
                
                back_button = self.driver.find_element(By.CSS_SELECTOR, "div.popup__header__back")
                self.driver.execute_script("arguments[0].click();", back_button)
            except:
                pass

        if "Review Count" in requested_fields:
            try:
                review_section = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__review")
                review_count_element = review_section.find_element(By.CSS_SELECTOR, "a.pdp__review--count")
                all_data["Review Count"] = review_count_element.text.split()[0]
            except:
                pass

        if "LandMarks" in requested_fields:
            try:
                landmark_section = self.driver.find_element(By.ID, "nearbylandmarksWeb")
                cards = landmark_section.find_elements(By.CLASS_NAME, "pdp__landmarks__card")
                landmarks_dict = {}
                
                for card in cards:
                    try:
                        category = card.find_element(By.CLASS_NAME, "pdp__landmarks__card__head").text.strip()
                        wraps = card.find_elements(By.CLASS_NAME, "pdp__landmarks__card--wrap")
                        landmarks = []
                        for wrap in wraps:
                            name = wrap.find_element(By.CLASS_NAME, "pdp__landmarks__card__item").text.strip()
                            distance = wrap.find_element(By.CLASS_NAME, "pdp__landmarks__card__item--bold").text.strip()
                            landmarks.append(f"{name} {distance}")
                        landmarks_dict[category] = ", ".join(landmarks)
                    except:
                        continue
                
                all_data["LandMarks"] = " | ".join([f"{cat}: {places}" for cat, places in landmarks_dict.items()])
            except:
                pass

        if "RERA Number" in requested_fields:
            try:
                faq_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "pdp__faq__ans")))
                for elem in faq_elements:
                    text = elem.text.strip()
                    if "RERA number" in text:
                        match = re.search(r'\[([A-Z0-9/\-]+)', text)
                        if match:
                            all_data["RERA Number"] = match.group(1)
                            break
            except:
                pass

        if "Video Count" in requested_fields:
            try:
                market_expert_section = self.driver.find_element(By.ID, "expertReveiw")
                video_elements = market_expert_section.find_elements(By.CLASS_NAME, "pdp__marketExpt__card")
                all_data["Video Count"] = len(video_elements)
            except:
                pass

        if "Builder Experience" in requested_fields:
            try:
                all_data["Builder Experience"] = self.driver.find_element(By.XPATH, "//div[contains(text(), 'experience')]/following-sibling::div").text.strip()
            except:
                pass

        # Filter the data to only include requested fields
        filtered_data = {field: all_data[field] for field in requested_fields if field in all_data}
        filtered_data["XID"] = xid
        filtered_data["URL"] = url

        # Extract floor plans if requested
        if "Floor Plans" in requested_fields:
            try:
                floor_plan_container = self.driver.find_element(By.CLASS_NAME, "pdp__florpripln__cards")
                floor_plan_cards = floor_plan_container.find_elements(By.CSS_SELECTOR, ".swiper-slide, .swiper-slide swiper-slide-next , .swiper-slide swiper-slide-prev, .swiper-slide swiper-slide-active")

                for index, card in enumerate(floor_plan_cards):
                    try:
                        unit_details = card.find_elements(By.CSS_SELECTOR, "div.pdp__florpripln--bhk span")
                        unit_size = unit_details[0].text.strip() if len(unit_details) > 0 else None
                        unit_type = unit_details[1].text.strip() if len(unit_details) > 1 else None

                        try:
                            area_type = card.find_element(By.CLASS_NAME, "pdp__florpripln--superArea").text.strip()
                        except:
                            area_type = None

                        try:
                            price = card.find_element(By.CLASS_NAME, "fullPrice__amount").text.strip()
                        except:
                            price = None

                        try:
                            possession_date = card.find_element(By.CLASS_NAME, "pdp__florpripln--possDate").text.strip()
                        except:
                            possession_date = None

                        if any([unit_size, unit_type, area_type, price, possession_date]):
                            floor_plans.append([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", 
                                              area_type or "Area Not Available", price or "Price Not Available", 
                                              possession_date or "Possession Not Available"])

                        if (index + 1) % 2 == 0:
                            try:
                                next_button = self.driver.find_element(By.ID, "fp-arrow-next")
                                self.driver.execute_script("arguments[0].click();", next_button)
                                time.sleep(2)
                            except:
                                break
                    except:
                        continue
            except:
                # try:
                #     alternative_floor_plan_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__prop__card")
                #     for card in alternative_floor_plan_cards:
                #         try:
                #             unit_details = card.find_element(By.CSS_SELECTOR, "div.pdp__prop__card__bhk span").text.strip()
                #             unit_type, unit_size = unit_details.split(" ", 1) if " " in unit_details else (unit_details, "Size Not Available")

                #             try:
                #                 price = card.find_element(By.CLASS_NAME, "pdp__prop__card__price").text.strip()
                #             except:
                #                 price = "Price Not Available"

                #             try:
                #                 possession_date = card.find_element(By.CLASS_NAME, "pdp__prop__card__cons").text.strip()
                #             except:
                #                 possession_date = "Possession Not Available"

                #             floor_plans.append([xid, unit_type, unit_size, "Area Not Available", price, possession_date])
                #         except:
                #             continue
                # except:
                pass

        return filtered_data, floor_plans


class HousingCrawler(BaseCrawler):
    def image_vdo_count(self, xid):
        output_data = []
        image_count = "Not Found"
        video_count = "Not Found"
        
        try:
            try:
                try:
                    photos = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[3]/div[3]/img")
                except:
                    photos = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[4]/div[3]/img[2]")
                photos.click()
                self.driver.implicitly_wait(5)
                count = self.driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]")
                image_count = count.text
            except:
                pass
    
            try:
                video = self.driver.find_element(By.XPATH, "/html/body/div/div[5]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[2]")
                if video.text == "Videos":
                    video.click()
                    v = self.driver.find_element(By.XPATH, "//*[@id='modal-root']/div/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]")
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
        
        imgvv["Final_Image_Count"] = img_count_list
        imgvv["Final_Video_Count"] = vv_count_list
        imgvv["Total_Media_Count"] = total_count_list
        
        imgvv.drop(columns=["image_count", "video_count"], inplace=True)
        
        return img_count_list[0], vv_count_list[0], total_count_list[0]

    def extract_project_data(self, xid, url, requested_fields):
        if not url:
            return None, None
            
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url

        all_data = {
            "XID": xid,
            "URL": url,
            "Project Name": "N/A",
            "Builder Name": "N/A",
            "Project Address": "N/A",
            "Avg Price psft": "N/A",
            "Completion date": "N/A",
            "Sizes": "N/A",
            "Project Area": "N/A",
            "RERA": "N/A",
            "Project Size - Tower Count": "N/A",
            "Project Size - Unit Count": "N/A",
            "Configurations": "N/A",
            "Amenities - Count": 0,
            "Amenities - List": "N/A",
            "Photos Count": "N/A",
            "Videos Count": "N/A",
            "Media Count": "N/A",
            "Review Count": 0,
            "Builder-Established Date": "N/A",
            "Builder-Project count": "N/A",
            "Builder description": "N/A",
            "Possession Status": "N/A",
            "Launch Date": "N/A",
            "Price trends": "N/A"
        }
        
        floor_plans = []

        try:
            self.driver.get(url)
            time.sleep(5)

            try:
                ok_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
                )
                self.driver.execute_script("arguments[0].click();", ok_button)
            except:
                pass

            time.sleep(5)

            if "Project Name" in requested_fields:
                try:
                    all_data["Project Name"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1').text.strip()
                except:
                    pass

            if "Builder Name" in requested_fields:
                try:
                    all_data["Builder Name"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/a/span').text.strip()
                except:
                    pass

            if "Project Address" in requested_fields:
                try:
                    all_data["Project Address"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]').text.strip()
                except:
                    pass

            if "Avg Price psft" in requested_fields:
                try:
                    all_data["Avg Price psft"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/span[2]').text.strip()
                except:
                    pass

            if "Completion date" in requested_fields:
                try:
                    all_data["Completion date"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[2]/div[1]').text.strip()
                except:
                    pass

            if "Configurations" in requested_fields:
                try:
                    all_data["Configurations"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[1]/div[1]').text.strip()
                except:
                    pass

            if any(field in requested_fields for field in ["Builder-Established Date", "Builder-Project count", "Builder description"]):
                try:
                    buttons = [
                        "//*[@id='amenities']/div[2]/div[2]/div[3]/h3/div",
                        "//*[@id='amenities']/div[2]/div[2]/div[2]/h3/div",
                        "//*[@id='amenities']/div[1]/section/div/div[12]/div",
                        "//*[@id='aboutDeveloper']/div[1]/div/div[2]/div/span"
                    ]
                    for b in buttons:
                        try: 
                            wait.until(EC.element_to_be_clickable((By.XPATH, b))).click()
                        except: 
                            pass

                    if "Builder-Established Date" in requested_fields:
                        try:
                            all_data["Builder-Established Date"] = self.driver.find_element(By.XPATH, '//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[1]/div[1]').text.strip()
                        except:
                            pass

                    if "Builder-Project count" in requested_fields:
                        try:
                            all_data["Builder-Project count"] = self.driver.find_element(By.XPATH, '//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[2]/div[1]').text.strip()
                        except:
                            pass

                    if "Builder description" in requested_fields:
                        try:
                            all_data["Builder description"] = self.driver.find_element(By.XPATH, '//*[@id="aboutDeveloper"]/div[1]/div/div[2]/div/div').text.strip()
                        except:
                            pass
                except:
                    pass

            if any(field in requested_fields for field in ["Sizes", "Project Area", "RERA", "Project Size - Tower Count", "Project Size - Unit Count", "Launch Date", "Possession Starts"]):
                try:
                    raw = self.driver.find_element(By.XPATH, '//*[@id="overviewDetails"]/section/div/table/tbody').text.strip()
                    items = [i for i in raw.split("\n") if i.strip().lower() != "check rera status"]
                    pairs = {items[i]: items[i+1] for i in range(0, len(items)-1, 2)}
                    
                    if "Sizes" in requested_fields:
                        all_data["Sizes"] = pairs.get("Sizes", "N/A")
                    if "Project Area" in requested_fields:
                        all_data["Project Area"] = pairs.get("Project Area", "N/A")
                    if "RERA" in requested_fields:
                        all_data["RERA"] = pairs.get("Rera Id", "N/A")
                    if "Launch Date" in requested_fields:
                        all_data["Launch Date"] = pairs.get("Launch Date", "N/A")
                    if "Possession Starts" in requested_fields:
                        all_data["Possession Starts"] = pairs.get("Possession Starts", "N/A")

                    project_size_str = pairs.get("Project Size", "").lower()
                    tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', project_size_str)
                    unit_match = re.search(r'(\d+)\s*units?', project_size_str)

                    if "Project Size - Tower Count" in requested_fields:
                        all_data["Project Size - Tower Count"] = tower_match.group(1) if tower_match else "N/A"
                    if "Project Size - Unit Count" in requested_fields:
                        all_data["Project Size - Unit Count"] = unit_match.group(1) if unit_match else "N/A"
                except:
                    pass

            if "Possession Status" in requested_fields:
                try:
                    text1 = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
                    text2 = self.driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[1]")
                    if text1.text == text2.text:
                        all_data["Possession Status"] = self.driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]").text
                except:
                    pass

            if "Review Count" in requested_fields:
                try:
                    text1 = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
                    text2 = self.driver.find_element(By.XPATH, "//*[@id='reviewBanner']/section/div[1]/div[1]/div/span")
                    if text1.text == text2.text:
                        review = self.driver.find_element(By.CSS_SELECTOR, "#reviewBanner h2 > span")
                        all_data["Review Count"] = review.text
                except: 
                    pass

            if any(field in requested_fields for field in ["Photos Count", "Videos Count", "Media Count"]):
                try:
                    img_count, video_count, total_count = self.image_vdo_count(xid)
                    if "Photos Count" in requested_fields:
                        all_data["Photos Count"] = img_count
                    if "Videos Count" in requested_fields:
                        all_data["Videos Count"] = video_count
                    if "Media Count" in requested_fields:
                        all_data["Media Count"] = total_count
                except:
                    pass

            if "Amenities - List" in requested_fields or "Amenities - Count" in requested_fields:
                try:
                    amenities = self.driver.find_element(By.XPATH, '//*[@id="amenities"]/div').text.strip().split("\n")
                    amenities = [i for i in amenities if i.strip().lower() != "less"]
                    
                    if "Amenities - List" in requested_fields:
                        all_data["Amenities - List"] = ", ".join(amenities)
                    if "Amenities - Count" in requested_fields:
                        all_data["Amenities - Count"] = len(amenities)
                except:
                    pass

            if "Price trends" in requested_fields:
                try:
                    all_data["Price trends"] = self.driver.find_element(By.XPATH, '//*[@id="priceTrends"]/section/div[2]/div[4]/div[2]/div[2]/div[1]/div[3]/div[2]/div[1]').text.strip()
                except:
                    pass

            if "Floor Plans" in requested_fields:
                try:
                    list1 = self.driver.find_element(By.CLASS_NAME, "config-header-container.css-n0tp0a")
                    list_items = list1.find_elements(By.TAG_NAME, "li")
                    for item in list_items:
                        self.driver.execute_script("arguments[0].click();", item)
                        time.sleep(1)
                        config_item = item.text.strip()

                        previous_data = set()
                        while True:
                            try:
                                nested = self.driver.find_element(By.CLASS_NAME, "header-container.css-n0tp0a")
                                nested_items = nested.find_elements(By.TAG_NAME, "li")
                                current_data = set()
                                for sub in nested_items:
                                    list_text = sub.text.strip()
                                    current_data.add(list_text)
                                    self.driver.execute_script("arguments[0].click();", sub)
                                    time.sleep(1)
                                    try:
                                        price_element = self.driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div/div/div/div/div[1]/div[1]')
                                        price_text = price_element.text.strip()
                                    except:
                                        price_text = "Price not found"

                                    floor_plans.append([xid, all_data["Project Name"], config_item, list_text, price_text])

                                if current_data == previous_data:
                                    break
                                previous_data = current_data

                                try:
                                    next_btn = self.driver.find_element(By.XPATH, '//*[@id="floorPlan"]/div[2]/div/div/div/div[1]/div[2]')
                                    if "css-hskvoc" in next_btn.get_attribute("class"):
                                        break
                                    self.driver.execute_script("arguments[0].click();", next_btn)
                                    time.sleep(2)
                                except:
                                    break
                            except:
                                break
                except Exception as e:
                    print(f"Floor plan extraction failed for {xid}")

            # Filter the data to only include requested fields
            filtered_data = {field: all_data[field] for field in requested_fields if field in all_data}
            filtered_data["XID"] = xid
            filtered_data["URL"] = url

            return filtered_data, floor_plans

        except Exception as ex:
            print(f"Error on {xid}: {ex}")
            return None, None


class SquareYardsCrawler(BaseCrawler):
    def extract_project_data(self, xid, url, requested_fields):
        if not url:
            return None, None
            
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
        if not url.endswith("/project"):
            return None, None

        all_data = {
            "XID": xid,
            "URL": url,
            "Project Name": "N/A",
            "Builder Name": "N/A",
            "Location": "N/A",
            "Price Range": "N/A",
            "Price per Sqft": "N/A",
            "Configurations": "N/A",
            "Completion Date": "N/A",
            "Unit Size Range": "N/A",
            "LandMarks": "N/A",
            "Project Size": "N/A",
            "Launch Date": "N/A",
            "RERA Number": "N/A",
            "Total Number of Units": "N/A",
            "USP": "N/A",
            "BHK": "N/A",
            "Amenity Count": 0,
            "Amenities": "N/A",
            "Specifications": "N/A",
            "Photo Count": "N/A",
            "Video Count": "N/A",
            "Rating count": "N/A",
            "Price Trend": "N/A",
            "Builder URL": "N/A",
            "Builder Experience": "N/A",
            "Total Projects": "N/A",
            "Ongoing Projects": "N/A",
            "Past Projects": "N/A",
            "Builder Info": "N/A",
            "Project Status": "N/A"
        }
        
        floor_plans = []

        retries = 3
        for attempt in range(retries):
            try:
                print(f"Attempting to load URL (Attempt {attempt + 1}/{retries}): {url}")
                self.driver.get(url)
                time.sleep(3)
                break
            except Exception as e:
                print(f"Error loading URL {url} on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    return None, None

        try:
            # Handle potential popup
            try:
                time.sleep(5)
                popup_div = self.driver.find_element(By.ID, "ClientInfoForm_projectpopup_formbox")
                close_button = popup_div.find_element(By.CSS_SELECTOR, "button.closeButton")
                self.driver.execute_script("arguments[0].click();", close_button)
            except:
                pass

            if "Project Name" in requested_fields:
                try:
                    all_data["Project Name"] = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
                except:
                    pass

            if "Location" in requested_fields:
                try:
                    all_data["Location"] = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading .location").text.strip()
                except:
                    pass

            if "Price Range" in requested_fields:
                try:
                    all_data["Price Range"] = self.driver.find_element(By.CSS_SELECTOR, "div.npPriceBox").text.strip().replace("₹", "Rs")
                except:
                    pass

            if "Price per Sqft" in requested_fields:
                try:
                    all_data["Price per Sqft"] = self.driver.find_element(By.CSS_SELECTOR, "div.npPerSqft").text.strip().replace("₹", "Rs")
                except:
                    pass

            if "USP" in requested_fields:
                try:
                    view_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-link")
                    self.driver.execute_script("arguments[0].click();", view_more_button)
                    time.sleep(2)
                    try:
                        usp_elements = self.driver.find_elements(By.CSS_SELECTOR, ".whyConsiderContentModal .whyConsiderList li")
                        usps = [usp.text for usp in usp_elements]
                        all_data["USP"] = ",".join(usps)
                    except:
                        pass
                    close_button = self.driver.find_element(By.CSS_SELECTOR, "button.rightCloseButton")
                    self.driver.execute_script("arguments[0].click();", close_button)
                except:
                    pass

            if any(field in requested_fields for field in ["Project Status", "Configurations", "Unit Size Range", "Builder Name", 
                                                         "Total Number of Units", "Project Size", "Launch Date", "Completion Date"]):
                try:
                    table_cells = self.driver.find_elements(By.CSS_SELECTOR, "tbody td")
                    for cell in table_cells:
                        try:
                            label = cell.find_element(By.TAG_NAME, "span").text.strip()
                            value_element = cell.find_element(By.TAG_NAME, "strong")
                            value = value_element.text.strip() if not value_element.find_elements(By.TAG_NAME, "button") else "Ask for Details"

                            if label == "Builder" and "Builder Name" in requested_fields:
                                all_data["Builder Name"] = value
                                try:
                                    builder_link_element = value_element.find_element(By.TAG_NAME, "a")
                                    all_data["Builder URL"] = builder_link_element.get_attribute("href")
                                except:
                                    pass
                            elif label == "Project Status" and "Project Status" in requested_fields:
                                all_data["Project Status"] = value
                            elif label == "Configurations" and "Configurations" in requested_fields:
                                all_data["Configurations"] = value
                            elif label == "Unit Sizes" and "Unit Size Range" in requested_fields:
                                all_data["Unit Size Range"] = value
                            elif label == "Total Number of Units" and "Total Number of Units" in requested_fields:
                                all_data["Total Number of Units"] = value
                            elif label == "Project Size" and "Project Size" in requested_fields:
                                all_data["Project Size"] = value
                            elif label == "Launch Date" and "Launch Date" in requested_fields:
                                all_data["Launch Date"] = value
                            elif label == "Completion Date" and "Completion Date" in requested_fields:
                                all_data["Completion Date"] = value
                        except:
                            continue
                except:
                    pass

            if any(field in requested_fields for field in ["Builder Experience", "Total Projects", "Ongoing Projects", "Past Projects", "Builder Info"]):
                if "Builder URL" in all_data and all_data["Builder URL"] != "N/A":
                    try:
                        self.driver.execute_script("window.open(arguments[0]);", all_data["Builder URL"])
                        time.sleep(2)
                        self.driver.switch_to.window(self.driver.window_handles[1])
                        time.sleep(2)

                        if "Builder Experience" in requested_fields:
                            try:
                                all_data["Builder Experience"] = self.driver.find_element(By.CSS_SELECTOR, "div.totalExperience").text.strip()
                            except:
                                pass

                        if "Total Projects" in requested_fields:
                            try:
                                all_data["Total Projects"] = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[0].text.strip()
                            except:
                                pass

                        if "Ongoing Projects" in requested_fields:
                            try:
                                all_data["Ongoing Projects"] = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[1].text.strip()
                            except:
                                pass

                        if "Past Projects" in requested_fields:
                            try:
                                all_data["Past Projects"] = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[2].text.strip()
                            except:
                                pass

                        if "Builder Info" in requested_fields:
                            try:
                                label = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='expendBox']")))
                                self.driver.execute_script("arguments[0].scrollIntoView();", label)
                                self.driver.execute_script("arguments[0].click();", label)
                                time.sleep(1)
                                description = WebDriverWait(self.driver, 10).until(
                                    EC.presence_of_element_located((By.CSS_SELECTOR, ".whiteBody .descriptionBox p")))
                                all_data["Builder Info"] = description.text.strip()
                            except:
                                pass

                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    except:
                        pass

            if "Floor Plans" in requested_fields:
                try:
                    price_list_tab = self.driver.find_element(By.XPATH, "//li[@data-tab='npPriceList']")
                    self.driver.execute_script("arguments[0].click();", price_list_tab)
                    time.sleep(3)
                    
                    price_table = self.driver.find_element(By.CSS_SELECTOR, ".npTableBox.scrollBarHide.active")
                    rows = price_table.find_elements(By.CSS_SELECTOR, "tbody tr")

                    for row in rows:
                        try:
                            unit_type = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) strong").text.strip()
                            price = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span").text.strip().replace("₹", "Rs")
                            area_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) .bhkSqFt.Detail_NewProject_D11")
                            area = area_element.find_element(By.CSS_SELECTOR, "span").text.strip()
                            try:
                                area_type = area_element.find_element(By.CSS_SELECTOR, ".saleable.Detail_NewProject_D11").text.strip()
                            except:
                                area_type = "N/A"
                            floor_plans.append([xid, all_data["Project Name"], unit_type, area, price, area_type])
                        except:
                            continue
                except:
                    pass

            if "RERA Number" in requested_fields:
                try:
                    rera_panel = self.driver.find_element(By.CSS_SELECTOR, ".panelHeader[data-reraid]")
                    all_data["RERA Number"] = rera_panel.find_element(By.CSS_SELECTOR, "strong").text.split()[0].strip()
                except:
                    pass

            if "Specifications" in requested_fields:
                try:
                    spec_rows = self.driver.find_elements(By.CSS_SELECTOR, "#specifications .npSpecificationTable tbody tr")
                    specifications = []
                    for row in spec_rows:
                        try:
                            heading = row.find_element(By.CSS_SELECTOR, ".npSpecificationHeading strong").text.strip()
                            value = row.find_element(By.CSS_SELECTOR, ".npSpecificationValue span").text.strip()
                            specifications.append(f"{heading}: {value}")
                        except:
                            continue
                    all_data["Specifications"] = "; ".join(specifications) if specifications else "N/A"
                except:
                    pass

            if "Amenities" in requested_fields or "Amenity Count" in requested_fields:
                def extract_amenities(panel_name):
                    try:
                        panel_xpath = f"//div[contains(@class, 'panelHeader')]/strong[text()='{panel_name}']"
                        panel_elements = self.driver.find_elements(By.XPATH, panel_xpath)
                        if not panel_elements:
                            return []

                        panel_element = panel_elements[0]
                        panel_body_xpath = f"{panel_xpath}/parent::div/following-sibling::div[contains(@class, 'panelBody')]"
                        panel_body_elements = self.driver.find_elements(By.XPATH, panel_body_xpath)

                        if not panel_body_elements:
                            return []

                        panel_body = panel_body_elements[0]
                        is_expanded = "active" in panel_body.get_attribute("class")

                        if not is_expanded:
                            self.driver.execute_script("arguments[0].click();", panel_element)
                            time.sleep(2)

                        amenity_elements = panel_body.find_elements(By.CSS_SELECTOR, ".npAmenitiesTable tbody tr td span")
                        return [element.text.strip() for element in amenity_elements if element.text.strip()]
                    except:
                        return []

                amenities = []
                amenities.extend(extract_amenities("Sports"))
                amenities.extend(extract_amenities("Convenience"))
                amenities.extend(extract_amenities("Safety"))
                amenities.extend(extract_amenities("Leisure"))
                amenities.extend(extract_amenities("Environment"))

                if "Amenities" in requested_fields:
                    all_data["Amenities"] = "; ".join(amenities) if amenities else "N/A"
                if "Amenity Count" in requested_fields:
                    all_data["Amenity Count"] = len(amenities)

            if any(field in requested_fields for field in ["Photo Count", "Video Count"]):
                try:
                    all_images = self.driver.find_elements(By.CSS_SELECTOR, ".npMidBox .npFigure.loadGallery img")
                    image_count = len(all_images)

                    try:
                        badge_photo_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.moreImages .badge").text
                        if '+' in badge_photo_text and 'Photos' in badge_photo_text:
                            extra_photos = int(badge_photo_text.split('+')[1].split()[0])
                            image_count += extra_photos
                    except:
                        pass

                    try:
                        self.driver.find_element(By.CSS_SELECTOR, ".npLargeBox .npFigure img")
                        image_count += 1
                    except:
                        pass

                    if "Photo Count" in requested_fields:
                        all_data["Photo Count"] = image_count

                    if "Video Count" in requested_fields:
                        try:
                            badge_video_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.video .badge").text
                            if '+' in badge_video_text and 'Video' in badge_video_text:
                                all_data["Video Count"] = int(badge_video_text.split('+')[1].split()[0])
                            elif 'Video' in badge_video_text:
                                all_data["Video Count"] = 1
                        except:
                            pass
                except:
                    pass

            if "Price Trend" in requested_fields:
                try:
                    market_supply_sections = self.driver.find_elements(By.CSS_SELECTOR, ".npPiBox")
                    for section in market_supply_sections:
                        header = section.find_element(By.CLASS_NAME, "npPiHeader").text
                        if "Market Supply" in header:
                            items = section.find_elements(By.CLASS_NAME, "npPiItem")
                            for item in items:
                                if "₹" in item.text:
                                    all_data["Price Trend"] = item.text
                                    break
                            break
                except:
                    pass

            if "Rating count" in requested_fields:
                try:
                    rating_section = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".ratingBox"))
                    )
                    all_data["Rating count"] = self.driver.find_element(By.CSS_SELECTOR, ".ratingBox .strong").text.strip()
                except:
                    pass

            if "LandMarks" in requested_fields:
                try:
                    ul_element = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "nearLocation"))
                    )
                    landmark_list_items = ul_element.find_elements(By.TAG_NAME, "li")
                    landmarks = []
                    processed_landmarks = set()

                    for item in landmark_list_items:
                        try:
                            category = item.text.strip()
                            if category in processed_landmarks:
                                continue

                            self.driver.execute_script("arguments[0].click();", item)
                            time.sleep(2)

                            item_rows = self.driver.find_elements(By.CSS_SELECTOR, ".nearDistanceBox.active tbody tr")
                            item_list = []
                            item_set = set()

                            for row in item_rows:
                                try:
                                    name = row.find_element(By.CSS_SELECTOR, ".distanceTitle").text.strip()
                                    distance = row.find_element(By.CSS_SELECTOR, ".distance span").text.strip()
                                    item_key = (name, distance)
                                    if item_key not in item_set:
                                        item_list.append({"name": name, "distance": distance})
                                        item_set.add(item_key)
                                except:
                                    continue

                            if not any(l['category'] == category for l in landmarks):
                                landmarks.append({"category": category, "details": item_list})
                            processed_landmarks.add(category)

                            try:
                                view_less_button = self.driver.find_element(By.CSS_SELECTOR, ".nearDistanceBox.active .npBtnBox button")
                                self.driver.execute_script("arguments[0].click();", view_less_button)
                                time.sleep(2)
                            except:
                                pass
                        except:
                            continue

                    all_data["LandMarks"] = "; ".join([f"{item['category']}: {', '.join([f'{detail['name']} ({detail['distance']})' for detail in item['details']])}" for item in landmarks]) if landmarks else "N/A"
                except:
                    pass

            # Filter the data to only include requested fields
            filtered_data = {field: all_data[field] for field in requested_fields if field in all_data}
            filtered_data["XID"] = xid
            filtered_data["URL"] = url

            return filtered_data, floor_plans

        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            return None, None


class CrawlerUnifier:
    def __init__(self, site: str):
        self.site = site.lower()
        if self.site == "magicbricks":
            self.crawler = MagicBricksCrawler()
        elif self.site == "housing":
            self.crawler = HousingCrawler()
        elif self.site == "squareyards":
            self.crawler = SquareYardsCrawler()
        else:
            raise ValueError("Unsupported site. Choose from 'magicbricks', 'housing', or 'squareyards'.")

    def unify(self, input_csv, outputData_csv, fields=None, floor_plan_output=None):
        if fields is None:
            fields = []
            
        df = pd.read_csv(input_csv)
        column_map = {
            "magicbricks": "magicbricks.com link",
            "housing": "housing.com link",
            "squareyards": "squareyards.com link"
        }
        site_column = column_map[self.site]

        data = []
        floor_plans = []

        for _, row in df.iterrows():
            xid = row['XID']
            url = row.get(site_column, None)
            if pd.notna(url):
                try:
                    print(f"Processing XID: {xid}, URL: {url}")
                    row_data, floor_plan_data = self.crawler.extract_project_data(xid, url, fields)
                    if row_data:
                        data.append(row_data)
                    if floor_plan_data and floor_plan_output:
                        floor_plans.extend(floor_plan_data)
                except Exception as e:
                    print(f"Error processing {xid}: {e}")

        if data:
            output_df = pd.DataFrame(data)
            output_df.to_csv(outputData_csv, index=False)
            print(f"Saved output to {outputData_csv}")

        if floor_plans and floor_plan_output:
            floor_plan_df = pd.DataFrame(floor_plans)
            if self.site == "magicbricks":
                floor_plan_df.columns = ["XID", "Unit Type", "Unit Size", "Area Type", "Price", "Possession Date"]
            elif self.site == "housing":
                floor_plan_df.columns = ["XID", "Project Name", "Configuration", "List Item", "Price"]
            elif self.site == "squareyards":
                floor_plan_df.columns = ["XID", "Project Name", "Unit Type", "Area", "Price", "Area Type"]
                
            floor_plan_df.to_csv(floor_plan_output, index=False)
            print(f"Saved floor plans to {floor_plan_output}")

        self.crawler.quit()


# Example usage:
# For MagicBricks with specific fields
unifier = CrawlerUnifier("magicbricks")
unifier.unify("auditUrls.csv", "mb_data1.csv", 
             fields=["XID", "URL", "Project Name", "Builder Name", "Location", "Price Range", "Price psft", "Property Type", "Possesion Date", "LandMarks", "Project Size", "Size Range", "Launch Date", "RERA Number", "Tower Count", "Unit Count", "USP", "BHK", "Amenity Count", "Amenities", "Image Count", "Specifications", "Review Count", "Builder Experience", "Builder Total Projects", "Builder Ready to Move Projects", "Builder Ongoing Projects", "Builder Info", "Project Status", "Video Count", "Floor Plans"],
             floor_plan_output="mb_floor_plans1.csv")

# For Housing with specific fields
unifier2 = CrawlerUnifier("housing")
unifier2.unify("auditUrls.csv", "housing_data1.csv", 
              fields=["XID", "Project Name", "Builder Name", "Project Address", "Avg Price psft", "Completion date", "Sizes", "Project Area", "RERA", "Project Size - Tower Count", "Project Size - Unit Count", "Configurations", "Amenities - Count", "Amenities - List", "Photos Count", "Videos Count", "Media Count", "Review Count", "Builder-Established Date", "Builder-Project count", "Builder description", "Possession Status", "Launch Date", "Price trends", "Floor Plans"],
              floor_plan_output="housing_floor_plans1.csv")

# For SquareYards with specific fields
unifier3 = CrawlerUnifier("squareyards")
unifier3.unify("auditUrls.csv", "sy_data1.csv", 
              fields=["XID", "URL", "Project Name", "Builder Name", "Location", "Price Range", "Price per Sqft", "Configurations", "Completion Date", "Unit Size Range", "LandMarks", "Project Size", "Launch Date", "RERA Number", "Total Number of Units", "USP", "BHK", "Amenity Count", "Amenities", "Specifications", "Photo Count", "Video Count", "Rating count", "Price Trend", "Builder URL", "Builder Experience", "Total Projects", "Ongoing Projects", "Past Projects", "Builder Info", "Project Status", "Floor Plans"],
              floor_plan_output="sy_floor_plans1.csv")
