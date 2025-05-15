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
    def extract_project_data(self, xid: str, url: str):
        pass

    def quit(self):
        self.driver.quit()


class MagicBricksCrawler(BaseCrawler):
    def extract_project_data(self, xid, url):
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
            "Project Address": "N/A",
            "Avg Price psft": "N/A",
            "Property Type": "N/A",
            "Completion date": "N/A",
            "Unit Size Range": "N/A",
            "Project Area": "N/A",
            "RERA": "N/A",
            "Project Size - Tower Count": "N/A",
            "Project Size - Unit Count": "N/A",
            "Configs": "N/A",
            "Amenities - Count": 0,
            "Amenities - List": "N/A",
            "Photos": 0,
            "Videos": 0,
            "Review Count": 0,
            "Builder-Established Date": "N/A",
            "Builder-Project Count": "N/A",
            "Possesion Status": "N/A",
            "Launch Date": "N/A"
        }
        
        floor_plans = []
        
        print(f"Opening URL: {url} for XID: {xid}")
        self.driver.get(url)
        time.sleep(3)

        # Project Name
        try:
            all_data["Project Name"] = self.driver.find_element(By.CSS_SELECTOR, ".pdp__name h1").text.strip()
        except:
            pass

        # Photos (Image Count)
        try:
            img_count = self.driver.find_element(By.CSS_SELECTOR, ".pdp__imgcount").get_attribute("textContent").strip()
            all_data["Photos"] = int(re.search(r'\d+', img_count).group()) if re.search(r'\d+', img_count) else 0
        except:
            pass

        # Builder Name
        try:
            all_data["Builder Name"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__developerName").text.replace("By ", "").strip()
        except:
            pass

        # Builder Info
        try:
            developer_link_element = self.driver.find_element(By.CSS_SELECTOR, "div.about-developer__builder__heading a")
            developer_link = developer_link_element.get_attribute("href")
            
            if developer_link:
                self.driver.execute_script("arguments[0].click();", developer_link_element)
                time.sleep(3)
                self.driver.switch_to.window(self.driver.window_handles[1])
                
                # Builder-Project Count
                try:
                    all_data["Builder-Project Count"] = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Total Projects')]/following-sibling::div").text.strip()
                except:
                    pass
                
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
        except:
            pass

        # Project Address (Location)
        try:
            all_data["Project Address"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__location").text.strip()
        except:
            pass

        # Avg Price psft
        try:
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__prunitar--item")
            for item in items:
                try:
                    label = item.find_element(By.CLASS_NAME, "pdp__prunitar--label").text.strip()
                    if label == "Price/sq.ft":
                        all_data["Avg Price psft"] = item.find_element(By.CLASS_NAME, "pdp__prunitar--data").text.strip().replace("₹", "Rs")
                        break
                except:
                    continue
        except:
            pass

        # Configs (BHK)
        try:
            all_data["Configs"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__bhkposs--data span.pdp__bhkposs--bhk").text.strip()
        except:
            pass

        # Property Type, Completion date, Launch Date, Tower Count, Project Status
        try:
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in table_rows:
                try:
                    key = row.find_element(By.TAG_NAME, "td").text.strip()
                    value = row.find_elements(By.TAG_NAME, "td")[1].text.strip()
                    
                    if "Property Types" in key:
                        all_data["Property Type"] = value
                    elif "Possession Date" in key:
                        all_data["Completion date"] = value
                        all_data["Possesion Status"] = "Under Construction" if "202" in value or "202" in value else "Ready to Move"
                    elif "Launch Date" in key:
                        all_data["Launch Date"] = value
                    elif "Towers" in key:
                        all_data["Project Size - Tower Count"] = value
                    elif "Status" in key:
                        all_data["Project Status"] = value
                except:
                    continue
        except:
            pass

        # Project Area
        try:
            all_data["Project Area"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Project Size')]/following-sibling::td").text.strip()
        except:
            pass

        # Project Size - Unit Count
        try:
            all_data["Project Size - Unit Count"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Total Units')]/following-sibling::td").text.strip()
        except:
            pass

        # Unit Size Range
        try:
            all_data["Unit Size Range"] = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__florpripln--brief span.text-semibold").text.strip()
        except:
            try:
                super_area_element = self.driver.find_element(By.CSS_SELECTOR, "span.pdp__prop__card__bhk")
                super_area_text = super_area_element.text.strip()
                all_data["Unit Size Range"] = super_area_text.split()[-2] + " " + super_area_text.split()[-1]
            except:
                pass

        # Amenities - List and Amenities - Count
        try:
            view_amenities = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View Amenities')]"))
            )
            self.driver.execute_script("arguments[0].click();", view_amenities)
            time.sleep(3)
            
            amenities_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__maproject__amentext")
            amenities = [amenity.text.strip() for amenity in amenities_elements if amenity.text.strip()]
            
            all_data["Amenities - List"] = ", ".join(amenities)
            all_data["Amenities - Count"] = len(amenities)
                
            back_button = self.driver.find_element(By.XPATH, '//*[@id="moredetails"]/div[6]/div[1]/div[1]')
            self.driver.execute_script("arguments[0].click();", back_button)
        except:
            pass

        # RERA
        try:
            faq_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pdp__faq__ans")))
            for elem in faq_elements:
                text = elem.text.strip()
                if "RERA number" in text:
                    match = re.search(r'\[([A-Z0-9/\-]+)', text)
                    if match:
                        all_data["RERA"] = match.group(1)
                        break
        except:
            pass

        # Videos (Video Count)
        try:
            market_expert_section = self.driver.find_element(By.ID, "expertReveiw")
            video_elements = market_expert_section.find_elements(By.CLASS_NAME, "pdp__marketExpt__card")
            all_data["Videos"] = len(video_elements)
        except:
            pass

        # Review Count
        try:
            review_section = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__review")
            review_count_element = review_section.find_element(By.CSS_SELECTOR, "a.pdp__review--count")
            all_data["Review Count"] = int(review_count_element.text.split()[0])
        except:
            pass

        # Floor Plans
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
            pass

        return all_data, floor_plans


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

    def extract_project_data(self, xid, url):
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
            "Property Type": "N/A",
            "Completion date": "N/A",
            "Unit Size Range": "N/A",
            "Project Area": "N/A",
            "RERA": "N/A",
            "Project Size - Tower Count": "N/A",
            "Project Size - Unit Count": "N/A",
            "Configs": "N/A",
            "Amenities - Count": 0,
            "Amenities - List": "N/A",
            "Photos": 0,
            "Videos": 0,
            "Review Count": 0,
            "Builder-Established Date": "N/A",
            "Builder-Project Count": "N/A",
            "Possesion Status": "N/A",
            "Launch Date": "N/A"
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

            # Project Name
            try:
                all_data["Project Name"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1').text.strip()
            except:
                pass

            # Builder Name
            try:
                all_data["Builder Name"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[2]/a/span').text.strip()
            except:
                pass

            # Project Address
            try:
                all_data["Project Address"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[3]').text.strip()
            except:
                pass

            # Avg Price psft
            try:
                all_data["Avg Price psft"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/div[2]/div/div[2]/div[1]/span[2]').text.strip()
            except:
                pass

            # Completion date
            try:
                all_data["Completion date"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[2]/div[1]').text.strip()
            except:
                pass

            # Configs
            try:
                all_data["Configs"] = self.driver.find_element(By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[1]/div[1]').text.strip()
            except:
                pass

            # Builder Info
            try:
                buttons = [
                    "//*[@id='amenities']/div[2]/div[2]/div[3]/h3/div",
                    "//*[@id='amenities']/div[2]/div[2]/div[2]/h3/div",
                    "//*[@id='amenities']/div[1]/section/div/div[12]/div",
                    "//*[@id='aboutDeveloper']/div[1]/div/div[2]/div/span"
                ]
                for b in buttons:
                    try: 
                        self.wait.until(EC.element_to_be_clickable((By.XPATH, b))).click()
                    except: 
                        pass

                # Builder-Established Date
                try:
                    all_data["Builder-Established Date"] = self.driver.find_element(By.XPATH, '//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[1]/div[1]').text.strip()
                except:
                    pass

                # Builder-Project Count
                try:
                    all_data["Builder-Project Count"] = self.driver.find_element(By.XPATH, '//*[@id="aboutDeveloper"]/div[1]/div/div[1]/h3/div/div[2]/div[1]').text.strip()
                except:
                    pass

            except:
                pass

            # Property details from table
            try:
                raw = self.driver.find_element(By.XPATH, '//*[@id="overviewDetails"]/section/div/table/tbody').text.strip()
                items = [i for i in raw.split("\n") if i.strip().lower() != "check rera status"]
                pairs = {items[i]: items[i+1] for i in range(0, len(items)-1, 2)}
                
                # Property Type
                all_data["Property Type"] = pairs.get("Property Type", "N/A")
                
                # RERA
                all_data["RERA"] = pairs.get("Rera Id", "N/A")
                
                # Launch Date
                all_data["Launch Date"] = pairs.get("Launch Date", "N/A")
                
                # Possesion Status
                possession_date = pairs.get("Possession Starts", "N/A")
                all_data["Possesion Status"] = "Under Construction" if "202" in possession_date or "202" in possession_date else "Ready to Move"
                
                # Project Size details
                project_size_str = pairs.get("Project Size", "").lower()
                tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', project_size_str)
                unit_match = re.search(r'(\d+)\s*units?', project_size_str)

                all_data["Project Size - Tower Count"] = tower_match.group(1) if tower_match else "N/A"
                all_data["Project Size - Unit Count"] = unit_match.group(1) if unit_match else "N/A"
            except:
                pass

            # Unit Size Range
            try:
                all_data["Unit Size Range"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Sizes')]/following-sibling::td").text.strip()
            except:
                pass

            # Project Area
            try:
                all_data["Project Area"] = self.driver.find_element(By.XPATH, "//td[contains(text(), 'Project Area')]/following-sibling::td").text.strip()
            except:
                pass

            # Photos, Videos count
            try:
                img_count, video_count, _ = self.image_vdo_count(xid)
                all_data["Photos"] = img_count if img_count != "Not Found" else 0
                all_data["Videos"] = video_count if video_count != "Not Found" else 0
            except:
                pass

            # Review Count
            try:
                text1 = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
                text2 = self.driver.find_element(By.XPATH, "//*[@id='reviewBanner']/section/div[1]/div[1]/div/span")
                if text1.text == text2.text:
                    review = self.driver.find_element(By.CSS_SELECTOR, "#reviewBanner h2 > span")
                    all_data["Review Count"] = int(review.text) if review.text.isdigit() else 0
            except: 
                pass

            # Amenities - List and Amenities - Count
            try:
                amenities = self.driver.find_element(By.XPATH, '//*[@id="amenities"]/div').text.strip().split("\n")
                amenities = [i for i in amenities if i.strip().lower() != "less"]
                
                all_data["Amenities - List"] = ", ".join(amenities)
                all_data["Amenities - Count"] = len(amenities)
            except:
                pass

            # Floor Plans
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

            return all_data, floor_plans

        except Exception as ex:
            print(f"Error on {xid}: {ex}")
            return None, None


class SquareYardsCrawler(BaseCrawler):
    def extract_project_data(self, xid, url):
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
            "Project Address": "N/A",
            "Avg Price psft": "N/A",
            "Property Type": "N/A",
            "Completion date": "N/A",
            "Unit Size Range": "N/A",
            "Project Area": "N/A",
            "RERA": "N/A",
            "Project Size - Tower Count": "N/A",
            "Project Size - Unit Count": "N/A",
            "Configs": "N/A",
            "Amenities - Count": 0,
            "Amenities - List": "N/A",
            "Photos": 0,
            "Videos": 0,
            "Review Count": 0,
            "Builder-Established Date": "N/A",
            "Builder-Project Count": "N/A",
            "Possesion Status": "N/A",
            "Launch Date": "N/A"
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

            # Project Name
            try:
                all_data["Project Name"] = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
            except:
                pass

            # Project Address (Location)
            try:
                all_data["Project Address"] = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading .location").text.strip()
            except:
                pass

            # Avg Price psft
            try:
                all_data["Avg Price psft"] = self.driver.find_element(By.CSS_SELECTOR, "div.npPerSqft").text.strip().replace("₹", "Rs")
            except:
                pass

            # Property details from table
            try:
                table_cells = self.driver.find_elements(By.CSS_SELECTOR, "tbody td")
                for cell in table_cells:
                    try:
                        label = cell.find_element(By.TAG_NAME, "span").text.strip()
                        value_element = cell.find_element(By.TAG_NAME, "strong")
                        value = value_element.text.strip() if not value_element.find_elements(By.TAG_NAME, "button") else "Ask for Details"

                        if label == "Builder":
                            all_data["Builder Name"] = value
                        elif label == "Project Status":
                            all_data["Possesion Status"] = value
                        elif label == "Configurations":
                            all_data["Configs"] = value
                        elif label == "Unit Sizes":
                            all_data["Unit Size Range"] = value
                        elif label == "Total Number of Units":
                            all_data["Project Size - Unit Count"] = value
                        elif label == "Project Size":
                            all_data["Project Area"] = value
                            # Extract tower count from project size if available
                            tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', value.lower())
                            if tower_match:
                                all_data["Project Size - Tower Count"] = tower_match.group(1)
                        elif label == "Launch Date":
                            all_data["Launch Date"] = value
                        elif label == "Completion Date":
                            all_data["Completion date"] = value
                        elif label == "Property Type":
                            all_data["Property Type"] = value
                    except:
                        continue
            except:
                pass

            # Builder Info
            try:
                builder_url = None
                try:
                    builder_link_element = self.driver.find_element(By.XPATH, "//strong[contains(text(), 'Builder')]/following-sibling::strong/a")
                    builder_url = builder_link_element.get_attribute("href")
                except:
                    pass

                if builder_url:
                    self.driver.execute_script("window.open(arguments[0]);", builder_url)
                    time.sleep(2)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(2)

                    # Builder-Established Date
                    try:
                        all_data["Builder-Established Date"] = self.driver.find_element(By.CSS_SELECTOR, "div.totalExperience").text.strip()
                    except:
                        pass

                    # Builder-Project Count
                    try:
                        all_data["Builder-Project Count"] = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[0].text.strip()
                    except:
                        pass

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass

            # RERA
            try:
                rera_panel = self.driver.find_element(By.CSS_SELECTOR, ".panelHeader[data-reraid]")
                all_data["RERA"] = rera_panel.find_element(By.CSS_SELECTOR, "strong").text.split()[0].strip()
            except:
                pass

            # Amenities - List and Amenities - Count
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

            all_data["Amenities - List"] = "; ".join(amenities) if amenities else "N/A"
            all_data["Amenities - Count"] = len(amenities)

            # Photos and Videos count
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

                all_data["Photos"] = image_count

                try:
                    badge_video_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.video .badge").text
                    if '+' in badge_video_text and 'Video' in badge_video_text:
                        all_data["Videos"] = int(badge_video_text.split('+')[1].split()[0])
                    elif 'Video' in badge_video_text:
                        all_data["Videos"] = 1
                except:
                    pass
            except:
                pass

            # Review Count
            try:
                rating_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ratingBox"))
                )
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ratingBox"))
                all_data["Review Count"] = self.driver.find_element(By.CSS_SELECTOR, ".ratingBox .strong").text.strip()
            except:
                pass

            # Floor Plans
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

            return all_data, floor_plans

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

    def unify(self, input_csv, outputData_csv, floor_plan_output=None):
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
                    row_data, floor_plan_data = self.crawler.extract_project_data(xid, url)
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
# For MagicBricks
unifier = CrawlerUnifier("magicbricks")
unifier.unify("auditUrls.csv", "mb_data3.csv", "mb_floor_plans3.csv")

# For Housing
unifier2 = CrawlerUnifier("housing")
unifier2.unify("auditUrls.csv", "housing_data3.csv", "housing_floor_plans3.csv")

# For SquareYards
unifier3 = CrawlerUnifier("squareyards")
unifier3.unify("auditUrls.csv", "sy_data3.csv", "sy_floor_plans3.csv")