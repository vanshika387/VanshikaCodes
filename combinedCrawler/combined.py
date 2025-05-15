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

        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url  # Add http:// if missing
            if not 'pdpid' in url:
                return

        floor_plans = []
        data_list = []
        print(f"Opening URL: {url} for XID: {xid} ")
        self.driver.get(url)
        time.sleep(3)  # Wait for elements to load

        operating_cities = "N/A"
        experience = "N/A"
        deals_property = "N/A"
        office_address = "N/A"
        total_projects = "N/A"
        completed_projects = "N/A"
        projects_ongoing = "N/A"
        builder_info = "N/A"
        joined_usps = "N/A"
        joined_location_advantages = "N/A"
        specifications_text = "N/A"

        # Extracting data
        try:
            project_name = self.driver.find_element(By.CSS_SELECTOR, ".pdp__name h1").text.strip()
        except:
            project_name = "N/A"

        # Extract image count
        try:
            
            img_count = self.driver.find_element(By.CSS_SELECTOR, ".pdp__imgcount").get_attribute("textContent").strip()
            print("Image Count:", img_count)
        except:
            img_count = "N/A"

        

        try:
            builder = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__developerName").text.replace("By ", "").strip()
        except:
            builder = "N/A"

        try:
            developer_link_element = self.driver.find_element(By.CSS_SELECTOR, "div.about-developer__builder__heading a")
            developer_link = developer_link_element.get_attribute("href")
        except:
            developer_link = "N/A"

        try:
            total_projects_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Total Projects')]/following-sibling::div")
            total_projects = total_projects_element.text.strip()
            print(total_projects)
        except:
            total_projects = "N/A"

        try:
            completed_projects_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Projects Completed')]/following-sibling::div")
            completed_projects = completed_projects_element.text.strip()
            print(completed_projects)
        except:
            completed_projects = "N/A"

        try:
            projects_ongoing_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Projects Ongoing')]/following-sibling::div")
            projects_ongoing = projects_ongoing_element.text.strip()  
            print(projects_ongoing)  
        except:
            projects_ongoing = "N/A"

        try:
            
            self.driver.execute_script("arguments[0].click();", developer_link_element)
            time.sleep(3)  # Wait for builder section to load
            print("Clicked 'Explore Builder' successfully.")
            # Switch to the new tab
            self.driver.switch_to.window(self.driver.window_handles[1])
            
            try:
                operating_cities_element = self.driver.find_element(By.CLASS_NAME, "dev-detail__overview__operating--less-content")
                operating_cities = operating_cities_element.text.strip()
            except:
                operating_cities = "N/A"

            try:
                # Get all label-value item pairs
                items = self.driver.find_elements(By.CSS_SELECTOR, ".dev-detail__overview__deals__list--item")

                experience_text = "N/A"
                for item in items:
                    label = item.find_element(By.CSS_SELECTOR, ".dev-detail__overview__deals__list--item--label").text.strip()
                    value = item.find_element(By.CSS_SELECTOR, ".dev-detail__overview__deals__list--item--value").text.strip()
                    if "experience" in label.lower():
                        experience_text = value
                        break

            except Exception as e:
                experience_text = "N/A"
                print("Error:", e)



            try:
                deals_property_element = self.driver.find_element(By.XPATH, "//div[contains(text(), 'Deals in Property Type')]/following-sibling::div")
                deals_property = deals_property_element.text.strip()
            except:
                deals_property = "N/A"

            try:
                office_address_element = self.driver.find_element(By.CSS_SELECTOR, "div.dev-detail__overview__address--value")
                office_address = office_address_element.text.strip()
            except:
                office_address = "N/A"


            # Close the new tab and switch back to the original tab
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            print(f"Operating in Cities: {operating_cities}")
        except:
            print("'Explore Builder' link not found or could not be clicked.")

        try:
            address = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__location").text.strip()
        except:
            address = "N/A"

        try:
            # price_range_element = driver.find_element(By.CSS_SELECTOR, "div.pdp__pricecard--price")
            # price_range = price_range_element.text.strip()
            # price_range = price_range.replace("₹", "Rs").strip()
            # print(price_range)
            price = self.driver.find_element(By.XPATH, '//*[@id="nav-overview"]/div[2]/div[1]/div[1]/div').text.strip()
            price = price.replace("₹", "Rs").strip()
            print(price)
        except:
            price = "N/A"

        try:
            flat_type = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__bhkposs--data span.pdp__bhkposs--bhk").text.strip()
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
            items = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__prunitar--item")
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
            super_area_element = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__florpripln--brief span.text-semibold")
            super_area = super_area_element.text.strip()
        except:
            try:
                super_area_element = self.driver.find_element(By.CSS_SELECTOR, "span.pdp__prop__card__bhk")
                super_area_text = super_area_element.text.strip()
                super_area = super_area_text.split()[-2] + " " + super_area_text.split()[-1]  # Extract the sq.ft part
            except:
                super_area = "N/A"



        try:
            view_amenities = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'View Amenities')]"))
            )
            self.driver.execute_script("arguments[0].click();", view_amenities)
            time.sleep(3)  # Wait for amenities section to load
        except:
            print("View Amenities' button not found or could not be clicked.")
        

        amenities = []
        try:
            amenities_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__maproject__amentext")
            amenities = [amenity.text.strip() for amenity in amenities_elements if amenity.text.strip()]
        except:
            pass

        amenity_count = len(amenities)

        try:
            back_button = self.driver.find_element(By.XPATH, '//*[@id="moredetails"]/div[6]/div[1]/div[1]')
            self.driver.execute_script("arguments[0].click();", back_button)
            print(" Back button clicked successfully.")
        except:
            print(" Back button not found.")

        try:
            usp_header = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Why Buy in')]"))
            )

            # Locate the parent div that contains the USPs
            usp_section = usp_header.find_element(By.XPATH, "./following-sibling::div")

            # Extract all list items (USPs + Location Advantages)
            usp_elements = usp_section.find_elements(By.TAG_NAME, "li")

            usps = []

            for li in usp_elements:
                text = li.text.strip()
                if text:
                    usps.append(text)

            # Join all USPs including location advantages into a single string
            joined_usps = " | ".join(usps)
            print(f"USPs: {joined_usps}")
        except:
            joined_usps = "N/A"

        try:
            print("Extracting Specifications...")

            # Locate the specification section
            try:
                spec_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'pdp__maproject__spaecdd')]/div[contains(@class, 'pdp__maproject__spaceContent')]"))
                )
                print(" Specifications section found.")
                specifications = []

                # Case 1: UL with <br> separators
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
                            break  # Stop checking other cases if extraction is successful

                except Exception as e:
                    print(f"Error in Nested UL Extraction: {str(e)}")

            # Case 2: Extract specifications from <ul> with <br> separators (if UL exists and Case 1 failed)
                if not specifications:
                    try:
                        ul_element = spec_section.find_element(By.TAG_NAME, "ul")
                        raw_text = ul_element.get_attribute("innerHTML")
                        if "<br>" in raw_text:
                            extracted_text = [line.strip() for line in raw_text.split("<br>") if line.strip()]
                            specifications.extend(extracted_text)
            
                    except:
                        pass  # If not found, move to next case

                if not specifications:
                    try:
                        ul_element = spec_section.find_element(By.TAG_NAME, "ul")  # Find UL containing divs
                        div_elements = ul_element.find_elements(By.TAG_NAME, "div")  # Get all divs inside UL

                        current_category = None
                        current_subcategory = None

                        for div in div_elements:
                            text = div.text.strip()

                            if text:
                                if not current_category:
                                    current_category = text  # First div is main category
                                elif not current_subcategory:
                                    current_subcategory = text  # Second div is subcategory
                                else:
                                    # Third div onwards is the value
                                    formatted_entry = f"{current_category} → {current_subcategory} → {text}"
                                    specifications.append(formatted_entry)
                                    current_subcategory = None  # Reset for the next subcategory
                    except Exception as e:
                        print(f"Error in UL with Div Extraction: {str(e)}")


                

                # Convert list to a single string with newlines
                specifications_text = "\n".join(specifications) if specifications else "N/A"

            except:
                specifications_text = "N/A"

        except:
            specifications = "N/A"

        try:
            read_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "readmore"))
            )
            self.driver.execute_script("arguments[0].click();", read_more_button)
            time.sleep(2)  # Wait for expanded content to load
            print("Clicked 'Read More' successfully.")
            try:
                builder_info_element = self.driver.find_element(By.CSS_SELECTOR, "div.popup__body.aboutdeveloper")
                builder_info = builder_info_element.text.strip()
            except:
                builder_info = "N/A"
            try:
                back_button = self.driver.find_element(By.CSS_SELECTOR, "div.popup__header__back")
                self.driver.execute_script("arguments[0].click();", back_button)
                print("Back button clicked successfully.")
            except:
                print("Back button not found.")
        except:
            builder_info = "N/A"
            print("'Read More' button not found or could not be clicked.")


        try:
            read_more = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Read More')]"))
            )
            self.driver.execute_script("arguments[0].click();", read_more)
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
            table_rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
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
            back_button = self.driver.find_element(By.CSS_SELECTOR, "div.popup__header__back")
            self.driver.execute_script("arguments[0].click();", back_button)
        
            print(" Back button clicked successfully.")
        except:
            print(" Back button not found.")

        try:
            
            print("Extracting Floor Plans...")
    # Locate the main container with class 'pdp__florpripln__cards'
            try:
                floor_plan_container = self.driver.find_element(By.CLASS_NAME, "pdp__florpripln__cards")
                
                # Find all floor plan cards inside the container
                floor_plan_cards = floor_plan_container.find_elements(By.CSS_SELECTOR, ".swiper-slide, .swiper-slide swiper-slide-next , .swiper-slide swiper-slide-prev, .swiper-slide swiper-slide-active")

                for index, card in enumerate(floor_plan_cards):
                    try:
                        # Extract unit size and type
                        unit_details = card.find_elements(By.CSS_SELECTOR, "div.pdp__florpripln--bhk span")
                        unit_size = unit_details[0].text.strip() if len(unit_details) > 0 else None
                        unit_type = unit_details[1].text.strip() if len(unit_details) > 1 else None

                        # Extract area type
                        try:
                            area_type = card.find_element(By.CLASS_NAME, "pdp__florpripln--superArea").text.strip()
                        except:
                            area_type = None

                        # Extract price
                        try:
                            price = card.find_element(By.CLASS_NAME, "fullPrice__amount").text.strip()
                        except:
                            price = None

                        # Extract possession date
                        try:
                            possession_date = card.find_element(By.CLASS_NAME, "pdp__florpripln--possDate").text.strip()
                        except:
                            possession_date = None

                        if any([unit_size, unit_type, area_type, price, possession_date]):
                            floor_plans.append([xid, unit_type or "Type Not Available", unit_size or "Size Not Available", area_type or "Area Not Available", price or "Price Not Available", possession_date or "Possession Not Available"])

                        
                        
                        # Only append if at least one of the key details is present
                    
                    except Exception as e:
                        print(f"Skipping a card due to error: {e}")

                    # Click the next button after every 2 records
                    if (index + 1) % 2 == 0:
                        try:
                            next_button = self.driver.find_element(By.ID, "fp-arrow-next")
                            self.driver.execute_script("arguments[0].click();", next_button)
                            time.sleep(2)  # Wait for the next set of floor plans to load
                        except:
                            print("Next button not found or could not be clicked.")
                            break

            except:
                # If no floor plan cards are found, try extracting from the alternative section
                if not floor_plans:
                    try:
                        print("hi")
                        alternative_floor_plan_cards = self.driver.find_elements(By.CSS_SELECTOR, "div.pdp__prop__card")
                        for card in alternative_floor_plan_cards:
                            try:
                                # Extract unit type and size
                                unit_details = card.find_element(By.CSS_SELECTOR, "div.pdp__prop__card__bhk span").text.strip()
                                unit_type, unit_size = unit_details.split(" ", 1) if " " in unit_details else (unit_details, "Size Not Available")

                                # Extract price
                                try:
                                    price = card.find_element(By.CLASS_NAME, "pdp__prop__card__price").text.strip()
                                except:
                                    price = "Price Not Available"

                                # Extract possession date
                                try:
                                    possession_date = card.find_element(By.CLASS_NAME, "pdp__prop__card__cons").text.strip()
                                except:
                                    possession_date = "Possession Not Available"

                                # Append extracted details
                                floor_plans.append([xid,  unit_type, unit_size, "Area Not Available", price, possession_date])
                            except Exception as e:
                                print(f"Skipping an alternative card due to error: {e}")
                    except:
                        print("No alternative floor plan section found.")
                print("No floor plan container found on this page.")


            # Print extracted floor plans for debugging
            for plan in floor_plans:
                print(plan)

        except Exception as e:
            print(f"Error extracting floor plans: {e}")

        

        # Extract review count and rating
        try:
            review_section = self.driver.find_element(By.CSS_SELECTOR, "div.pdp__review")
            review_count_element = review_section.find_element(By.CSS_SELECTOR, "a.pdp__review--count")
            review_count = review_count_element.text.split()[0]  # Extract the number of reviews
            print(f"Review Count: {review_count}")

        except:
            review_count = "N/A"
            
        landmarks_dict = {}

        try:
            landmark_section = self.driver.find_element(By.ID, "nearbylandmarksWeb")
            cards = landmark_section.find_elements(By.CLASS_NAME, "pdp__landmarks__card")
            
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
        except Exception as e:
            print("❌ Error extracting landmarks:", e)

        # Format into single string: Category: landmarks...
        formatted_landmarks = " | ".join([f"{cat}: {places}" for cat, places in landmarks_dict.items()])
        print("Landmarks:", formatted_landmarks)

    
        try:
            # Wait for presence of multiple FAQ answer elements
            faq_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pdp__faq__ans"))
            )

            rera_number = "Not found"

            # Loop through each element and find the one with RERA info
            for elem in faq_elements:
                text = elem.text.strip()
                if "RERA number" in text:
                    match = re.search(r'\[([A-Z0-9/\-]+)', text)
                    if match:
                        rera_number = match.group(1)
                        break  # Exit after finding the first valid RERA number

        except Exception as e:
            rera_number = "N/A"
            print("Error:", e)

        print("RERA Number:", rera_number)

        try:
        # Wait until the span with class 'sarange' is available
            super_area_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sarange"))
            )

            # Extract the inner span that contains the value
            area_text = super_area_element.find_element(By.CLASS_NAME, "text-semibold").text.strip()

        except Exception as e:
            area_text = "N/A"
            print("Error:", e)

        # Extract number of videos from Market Expert Reviews section
        try:
            market_expert_section = self.driver.find_element(By.ID, "expertReveiw")
            video_elements = market_expert_section.find_elements(By.CLASS_NAME, "pdp__marketExpt__card")
            video_count = len(video_elements)
            print(f"Number of videos: {video_count}")
        except:
            video_count = "N/A"


        # Append data to list
        data_list.append([
            xid, url, project_name, builder,address,price,property_details["Price/sq.ft"],property_details2["Property Type"],property_details2["Possession Date"],formatted_landmarks,property_details["Project Size"],area_text,property_details2["Launch Date"],rera_number,property_details2["Total Towers"], property_details["Total Units"],joined_usps,flat_type, amenity_count,", ".join(amenities),img_count,specifications_text,review_count,experience_text, total_projects, completed_projects, projects_ongoing, builder_info,property_details2["Status"], video_count ])

        # Save to CSV simultaneously
        output_file = "DataMagicBricks.csv"
        with open(output_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if f.tell() == 0:  # Check if file is empty to write header
                writer.writerow([
                    "XID", "URL", "Project Name", "Builder Name","Location","Price Range","Price psft","Property Type","Possesion Date","LandMarks","Project Size","Size Range","Launch Date","RERA Number","Tower Count","Unit Count","USP","BHK","Amenity Count","Amenities","Image Count","Specifications","Review Count","Builder Experience", "Builder Total Projects", "Builder Ready to Move Projects", "Builder Ongoing Projects", "Builder Info","Project Status", "Video Count"])
            writer.writerow(data_list[-1])

        floor_plans_csv = "magicbricks_floorplans.csv"
        with open(floor_plans_csv, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # Check if file is empty to write header
                writer.writerow(["XID", "Unit Type", "Unit Size", "Area Type", "Price", "Possession Date"])
            # Write data
            writer.writerows(floor_plans)


class HousingCrawler(BaseCrawler):
    def image_vdo_count(self, xid):
        output_data = []  # Initialize output_data as an empty list
        image_count = "Not Found"  # Initialize image_count to avoid undefined variable error
        video_count = "Not Found"  # Initialize video_count to avoid undefined variable error
        
        try:
    
            # Try extracting image count
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
    
            # Try extracting video count
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


    def extract_project_data(self, xid, url, requested_fields):
        
        data = {field: "N/A" for field in requested_fields}

        try:
            self.driver.get(url)
            time.sleep(5)

            try:
                ok_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/button'))
                )
                self.driver.execute_script("arguments[0].click();", ok_button)
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
                try: return self.driver.find_element(By.XPATH, xpath).text.strip()
                except: return "Not Found"

            data = {
                "XID": xid,
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
                "Price trends": get_text('//*[@id="priceTrends"]/section/div[2]/div[4]/div[2]/div[2]/div[1]/div[3]/div[2]/div[1]')
                # "Possession Status": get_text('//*[@id="innerApp"]/div[2]/div[1]/div[1]/div/section/div[2]/div[1]')
            }

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
            # data["Possession Status"] = pairs.get("Possession Status", None)
            data["Possession Starts"] = pairs.get("Possession Starts", None)

            project_size_str = pairs.get("Project Size", "").lower()
            tower_match = re.search(r'(\d+)\s*(?:Towers?|Buildings?)', project_size_str)
            unit_match = re.search(r'(\d+)\s*units?', project_size_str)

            data["Project Size - Tower Count"] = tower_match.group(1) if tower_match else None
            data["Project Size - Unit Count"] = unit_match.group(1) if unit_match else None

            try:
                text1 = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
                text2 = self.driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[1]")
                if text1.text == text2.text:
                    data["Possession Status"] = self.driver.find_element(By.XPATH, "//*[@id='compareProperties']/div/div/div[2]/div[1]/div[2]/div[4]/div[1]/div[2]").text
            except:
                data["Possession Status"] = "Not Found"

            
            data["Review Count"] = 0

            try:
                text1 = self.driver.find_element(By.XPATH, "//*[@id='innerApp']/div[2]/div[1]/div[1]/div/div[2]/div/div[1]/div[1]/div/h1")
                text2 = self.driver.find_element(By.XPATH, "//*[@id='reviewBanner']/section/div[1]/div[1]/div/span")
                if text1.text == text2.text:
                    review = self.driver.find_element(By.CSS_SELECTOR, "#reviewBanner h2 > span")
                    data["Review Count"] = review.text
            except: pass

            image_count, video_count, total_count = self.image_vdo_count(xid)

            # Write housing data row
            
            housing_output_file = "DataHousing.csv"
            with open(housing_output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if( f.tell() == 0):  # Check if file is empty
                    # Write header only if the file is empty
                    writer.writerow([
                        'Project Name', 'Builder Name', 'Project Address', 'Avg Price psft', 'Completion date',
                        'Sizes', 'Project Area', 'RERA', 'Project Size - Tower Count', 'Project Size - Unit Count',
                        'Configurations', 'Amenities - Count', 'Amenities - List',
                        'Photos Count', 'Videos Count', 'Media Count', 'Review Count',
                        'Builder-Established Date', 'Builder-Project count', 'Builder description',
                        'Possession Status', 'Launch Date', 'Price trends'
                    ])

            # Prepare CSV writer for floor plan
            floorplan_output_file = 'floorPlanHousing.csv'
            with open(floorplan_output_file, 'a', newline='', encoding='utf-8') as outcsv:
                writer = csv.writer(outcsv)
                if outcsv.tell() == 0:
                    writer.writerow(['XID', 'Project Name', 'Configuration', 'List Item', 'Price'])
            with open(housing_output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    data["Project Name"], data["Builder Name"], data["Project Address"], data["Avg Price psft"], data["Completion date"],
                    data["Sizes"], data["Project Area"], data["RERA"], data["Project Size - Tower Count"], data["Project Size - Unit Count"],
                    data["Configurations"], data["Amenities - Count"], data["Amenities - List"],
                    image_count, video_count, total_count, data["Review Count"],
                    data["Builder-Established Date"], data["Builder-Project count"], data["Builder description"],
                    data["Possession Status"], data["Launch Date"], data["Price trends"]
                ])

            # ========== FLOOR PLAN SECTION ==========
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

                                # floorplan_output_file = "floorplan_output.csv"  # Define the output file path
                                with open(floorplan_output_file, 'a', newline='', encoding='utf-8') as outcsv:
                                    writer = csv.writer(outcsv)
                                    writer.writerow([xid, data["Project Name"], config_item, list_text, price_text])

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

        except Exception as ex:
            print(f"Error on {xid}")
            # continue


class SquareYardsCrawler(BaseCrawler):
    def extract_project_data(self, xid, url, requested_fields):

        def extract_amenities(panel_name):
            amenities = []
            try:
                panel_xpath = f"//div[contains(@class, 'panelHeader')]/strong[text()='{panel_name}']"
                panel_elements = self.driver.find_elements(By.XPATH, panel_xpath)

                if not panel_elements:
                    print(f"Panel '{panel_name}' not found on the page.")
                    return "N/A"

                panel_element = panel_elements[0]

                # Check if panel is already expanded
                panel_body_xpath = f"//div[contains(@class, 'panelHeader')]/strong[text()='{panel_name}']/parent::div/following-sibling::div[contains(@class, 'panelBody')]"
                panel_body_elements = self.driver.find_elements(By.XPATH, panel_body_xpath)

                if not panel_body_elements:
                    print(f"Panel body for '{panel_name}' not found.")
                    return "N/A"

                panel_body = panel_body_elements[0]
                is_expanded = "active" in panel_body.get_attribute("class")

                # Click only if it's not already expanded
                if not is_expanded:
                    self.driver.execute_script("arguments[0].click();", panel_element)
                    time.sleep(2)  # Wait for panel to expand

                # Extract amenities
                amenity_elements = panel_body.find_elements(By.CSS_SELECTOR, ".npAmenitiesTable tbody tr td span")
                for element in amenity_elements:
                    text = element.text.strip()
                    if text:
                        amenities.append(text)

            except Exception as e:
                print(f"Error extracting {panel_name} amenities: {e}")

            return "; ".join(amenities) if amenities else "N/A"

        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://" + url  # Add http:// if missing
            if not url.endswith("/project"):
                return

        retries = 3  # Number of retries for loading the page
        for attempt in range(retries):
            try:
                print(f"Attempting to load URL (Attempt {attempt + 1}/{retries}): {url}")
                self.driver.get(url)
                time.sleep(3)
                break  # Exit retry loop if successful
            except Exception as e:
                print(f"Error loading URL {url} on attempt {attempt + 1}: {e}")
                if attempt == retries - 1:
                    print(f"Failed to load URL after {retries} attempts: {url}")
                    continue  # Skip to the next URL

        try:
            # Handle potential popup
            
            try:
                project_name = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading strong").text.strip()
            except Exception:
                project_name = "N/A"

            # Extract location
            try:
                location = self.driver.find_element(By.CSS_SELECTOR, "h1.npMainHeading .location").text.strip()
            except Exception:
                location = "N/A"

            # Extract price range
            try:
                price_range = self.driver.find_element(By.CSS_SELECTOR, "div.npPriceBox").text.strip()
                price_range = price_range.replace("₹", "Rs").strip()
            except Exception:
                price_range = "N/A"

            # Extract price per square foot
            try:
                price_per_sqft = self.driver.find_element(By.CSS_SELECTOR, "div.npPerSqft").text.strip()
                price_per_sqft = price_per_sqft.replace("₹", "Rs").strip()
            except Exception:
                price_per_sqft = "N/A"
            
            

            # Extract "Why Consider" list items
            try:
                view_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-link")
                self.driver.execute_script("arguments[0].click();", view_more_button)
                time.sleep(2)
                try:
                    usp_elements = self.driver.find_elements(By.CSS_SELECTOR, ".whyConsiderContentModal .whyConsiderList li")
                    # Extract text
                    usps = [usp.text for usp in usp_elements]
                    #print("USP:", usps)
                    
                except Exception:
                    # 
                    usp=[]

                usp = ",".join(usps)
                print("USP:", usp)
                close_button = self.driver.find_element(By.CSS_SELECTOR, "button.rightCloseButton")
                self.driver.execute_script("arguments[0].click();", close_button)

            except Exception:
                usp = "N/A"

            try:
                time.sleep(5)  # Wait for the popup to appear
                popup_div = self.driver.find_element(By.ID, "ClientInfoForm_projectpopup_formbox")
                close_button = popup_div.find_element(By.CSS_SELECTOR, "button.closeButton")
                self.driver.execute_script("arguments[0].click();", close_button)
                print("Popup closed.")
            except Exception:
                print("No popup appeared.")

            try:
                price_per_sqft = self.driver.find_element(By.CSS_SELECTOR, "div.npPerSqft").text.strip()
                price_per_sqft = price_per_sqft.replace("₹", "Rs").strip()
            except Exception:
                price_per_sqft = "N/A"
            
            if usp == "N/A":
                try:
                    view_more_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-link")
                    self.driver.execute_script("arguments[0].click();", view_more_button)
                    time.sleep(2)
                    try:
                        usp_elements = self.driver.find_elements(By.CSS_SELECTOR, ".whyConsiderContentModal .whyConsiderList li")
                        # Extract text
                        usps = [usp.text for usp in usp_elements]
                        #print("USP:", usps)
                        
                    except Exception:
                        usp=[]

                    usp = ",".join(usps)
                    print("USP:", usp)
                    close_button = self.driver.find_element(By.CSS_SELECTOR, "button.rightCloseButton")
                    self.driver.execute_script("arguments[0].click();", close_button)

                except Exception:
                    usp = "N/A"

        

            #input("Press Enter to continue...")
            # Extract details dynamically from the table
            data_dict = {
                "Project Status": "N/A",
                "Configurations": "N/A",
                "Unit Sizes": "N/A",
                "Builder": "N/A",
                "Total Number of Units": "N/A",
                "Project Size": "N/A",
                "Launch Date": "N/A",
                "Completion Date": "N/A",
                "Locality": "N/A",
                "Micro Market": "N/A",
                "Builder Experience": "N/A",
                "Ongoing Projects": "N/A",
                "Past Projects": "N/A",
                "Builder URL": "N/A"
            }

            try:
                table_cells = self.driver.find_elements(By.CSS_SELECTOR, "tbody td")
                for cell in table_cells:
                    try:
                        label = cell.find_element(By.TAG_NAME, "span").text.strip()
                        value_element = cell.find_element(By.TAG_NAME, "strong")

                        if value_element.find_elements(By.TAG_NAME, "button"):
                            value = "Ask for Details"
                        else:
                            value = value_element.text.strip()

                        if label == "Builder":
                            try:
                                builder_link_element = value_element.find_element(By.TAG_NAME, "a")
                                data_dict["Builder URL"] = builder_link_element.get_attribute("href")
                            except Exception:
                                pass

                        data_dict[label] = value
                    except Exception:
                        pass
            except Exception:
                pass

            if data_dict["Builder URL"] != "N/A":
                try:
                    self.driver.execute_script("window.open(arguments[0]);", data_dict["Builder URL"])
                    time.sleep(2)
                    self.driver.switch_to.window(self.driver.window_handles[1])
                    time.sleep(2)

                    try:
                        builder_experience = self.driver.find_element(By.CSS_SELECTOR, "div.totalExperience").text.strip()
                    except Exception:
                        builder_experience = "N/A"

                    try:
                        ongoing_projects = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[0].text.strip()
                    except Exception:
                        ongoing_projects = "N/A"

                    try:
                        past_projects = self.driver.find_elements(By.XPATH, "//div[@class='totalProjectLi']/strong")[1].text.strip()
                    except Exception:
                        past_projects = "N/A"

                    try:
                        # Scroll to the section to ensure it's visible
                        label = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='expendBox']"))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView();", label)

                        # Click the label to expand
                        self.driver.execute_script("arguments[0].click();", label)
                        time.sleep(1)

                        # Wait and fetch the expanded description text
                        description = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, ".whiteBody .descriptionBox p"))
                        )
                        
                    
                        builder_info= description.text.strip()

                    except Exception as e:
                        builder_info = "N/A"
                        print(f"Error: {e}")

                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                except Exception:
                    builder_experience = "N/A"
                    ongoing_projects = "N/A"
                    past_projects = "N/A"
                    builder_info = "N/A"
            else:
                builder_experience = "N/A"
                ongoing_projects = "N/A"
                past_projects = "N/A"
                builder_info = "N/A"

            try:
                price_list_tab = self.driver.find_element(By.XPATH, "//li[@data-tab='npPriceList']")
                self.driver.execute_script("arguments[0].click();", price_list_tab)
                time.sleep(3)
            except Exception:
                print("Price List tab not found.")

            try:
                price_table = self.driver.find_element(By.CSS_SELECTOR, ".npTableBox.scrollBarHide.active")
                rows = price_table.find_elements(By.CSS_SELECTOR, "tbody tr")
            except Exception:
                print("No active price table found.")
                rows = []

            floor_plans = []
            for row in rows:
                try:

                    try:
                        unit_type = row.find_element(By.CSS_SELECTOR, "td:nth-child(1) strong").text.strip()
                    except Exception:
                        unit_type = "N/A"


                    try:
                        price = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) span").text.strip()
                        price = price.replace("₹", "Rs").strip()
                    except Exception:
                        price = "N/A"

                    area_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) .bhkSqFt.Detail_NewProject_D11")
                    area = area_element.find_element(By.CSS_SELECTOR, "span").text.strip()
                    print(area)
                    try:
                        area_type = area_element.find_element(By.CSS_SELECTOR, ".saleable.Detail_NewProject_D11").text.strip()
                        print(area_type)
                    except Exception:
                        area_type = "N/A"
                    floor_plans.append((unit_type, area, price, area_type))
                except Exception:
                    continue

            floor_plan_csv_filename = "squareyardsFloorPlans.csv"
            with open(floor_plan_csv_filename, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if not os.path.isfile(floor_plan_csv_filename) or os.stat(floor_plan_csv_filename).st_size == 0:
                    writer.writerow(["XID", "Project Name", "Unit Type", "Area", "Price", "Area Type"])
                for plan in floor_plans:
                    print("Floor Plan:", plan)
                    writer.writerow([xid, project_name, *plan])

            print(f"Floor plan data saved to {floor_plan_csv_filename}")

            try:
                rera_panel = self.driver.find_element(By.CSS_SELECTOR, ".panelHeader[data-reraid]")
                rera_number = rera_panel.get_attribute("data-reraid").strip()
            except Exception:
                rera_number = "N/A"

            specifications = []
            try:
                # Locate the specifications table
                spec_rows = self.driver.find_elements(By.CSS_SELECTOR, "#specifications .npSpecificationTable tbody tr")

                for row in spec_rows:
                    try:
                        # Extract heading
                        heading_element = row.find_element(By.CSS_SELECTOR, ".npSpecificationHeading strong")
                        heading = heading_element.text.strip() if heading_element else "N/A"

                        # Extract value
                        value_element = row.find_element(By.CSS_SELECTOR, ".npSpecificationValue span")
                        value = value_element.text.strip() if value_element else "N/A"

                        # Append to list only if value is not empty
                        if heading and value:
                            specifications.append(f"{heading}: {value}")
                    except Exception as row_error:
                        print("Error processing row:", row_error)

            except Exception as e:
                print("Error extracting specifications:", e)

            # Convert list to a string format
            specifications_text = "; ".join(specifications) if specifications else "N/A"

            print("Specifications:", specifications_text)

            sports_amenities = []
            try:
                # Locate the Sports panel
                sports_panel = self.driver.find_element(By.XPATH, "//div[contains(@class, 'panel')]/div[@class='panelHeader']/strong[text()='Sports']")
                
                # Get the parent panel div
                parent_panel = sports_panel.find_element(By.XPATH, "./ancestor::div[contains(@class, 'panel')]")
                
                # Check if the panel is already expanded (has 'active' class)
                is_expanded = "active" in parent_panel.get_attribute("class")
                
                # Click only if not expanded
                if not is_expanded:
                    self.driver.execute_script("arguments[0].click();", sports_panel)
                    time.sleep(2)  # Allow time for expansion
                
                # Now locate amenities inside the specific "Sports" panel
                sports_amenity_elements = parent_panel.find_elements(By.CSS_SELECTOR, ".panelBody .npAmenitiesTable tbody tr td span")
                
                for element in sports_amenity_elements:
                    text = element.text.strip()
                    if text:
                        sports_amenities.append(text)

            except Exception as e:
                print("Error extracting sports amenities:", e)

            # Convert amenities list to a string
            sports_amenities_text = "; ".join(sports_amenities) if sports_amenities else "N/A"

            
            convenience_amenities_text = extract_amenities("Convenience")
            

            safety_amenities_text = extract_amenities("Safety")
            

            leisure_amenities_text = extract_amenities("Leisure")
            

            environment_amenities_text = extract_amenities("Environment")
        


            amenities={sports_amenities_text, convenience_amenities_text, safety_amenities_text, environment_amenities_text, leisure_amenities_text}
            # Convert amenities set to a string
            amenities_text = "; ".join(amenities) if amenities else "N/A"
            print("Amenities:", amenities_text)
            

            amenity_count = len(amenities_text.split(";")) if amenities_text != "N/A" else 0
            print("Amenities Count:", amenity_count)

            # Count all visible image thumbnails
            all_images = self.driver.find_elements(By.CSS_SELECTOR, ".npMidBox .npFigure.loadGallery img")
            image_count = len(all_images)

            # Extract "+X Photos" from badge (if present)
            try:
                badge_photo_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.moreImages .badge").text
                if '+' in badge_photo_text and 'Photos' in badge_photo_text:
                    extra_photos = int(badge_photo_text.split('+')[1].split()[0])
                    image_count += extra_photos
            except:
                pass  # No badge, just stick with found images

            # Include the main large image
            try:
                self.driver.find_element(By.CSS_SELECTOR, ".npLargeBox .npFigure img")
                image_count += 1
            except:
                pass  # main image not present

            video_count = 0
            try:
                badge_video_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.video .badge").text
                if '+' in badge_video_text and 'Video' in badge_video_text:
                    video_count = int(badge_video_text.split('+')[1].split()[0])
            except:
                pass  # no video badge

            print("Image Count:", image_count)
            print("Video Count:", video_count)

            
            market_supply_sections = self.driver.find_elements(By.CSS_SELECTOR, ".npPiBox")

            price_trend = None

            for section in market_supply_sections:
                # Make sure this section is for 'Market Supply'
                header = section.find_element(By.CLASS_NAME, "npPiHeader").text
                print("Header:", header)
                if "Market Supply" in header:
                    items = section.find_elements(By.CLASS_NAME, "npPiItem")
                    for item in items:
                        print("Item Text:", item.text)
                        if "₹" in item.text:
                            price_trend = item.text
                            break
                    break

            print("Average Price (per sq.ft):", price_trend)

            try:
                # Wait until the rating section is present
                rating_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".ratingBox"))
                )
                rating_count = self.driver.find_element(By.CSS_SELECTOR, ".ratingBox .strong").text.strip()

                # Output
                
                print("Rating Count:", rating_count)

            except Exception as e:
                rating_count = "N/A"
                print("Error:", e)

                
            try:
                ul_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "nearLocation"))
                )

                # Get all <li> elements under the <ul>
                landmarks=[]
                landmark_list_items = ul_element.find_elements(By.TAG_NAME, "li")
                #landmark_rows = self.driver.find_elements(By.CSS_SELECTOR, ".nearLocation .npPiItem")
                # Extract the text from each <li> element
                for item in landmark_list_items:
                    text = item.text.strip()
                    if text:
                        print(text)
                c=0
                #Click on each landmark item to expand details (if clickable)
                processed_landmarks = set()  # Track processed landmark categories

                for item in landmark_list_items:
                    try:
                        category = item.text.strip()
                        if category in processed_landmarks:
                            continue  # Skip if already processed

                        self.driver.execute_script("arguments[0].click();", item)
                        print("Clicked on landmark item.")
                        time.sleep(2)

                        # Extract details
                        item_rows = self.driver.find_elements(By.CSS_SELECTOR, ".nearDistanceBox.active tbody tr")
                        item_list = []
                        item_set = set()  # Track unique items in the current landmark

                        for row in item_rows:
                            try:
                                name = row.find_element(By.CSS_SELECTOR, ".distanceTitle").text.strip()
                                distance = row.find_element(By.CSS_SELECTOR, ".distance span").text.strip()
                                item_key = (name, distance)  # Use a tuple as a unique identifier
                                if item_key not in item_set:
                                    item_list.append({"name": name, "distance": distance})
                                    item_set.add(item_key)
                            except:
                                continue

                        if not any(l['category'] == category for l in landmarks):
                            landmarks.append({"category": category, "details": item_list})
                        processed_landmarks.add(category)  # Mark as processed

                        # Collapse the section
                        try:
                            view_less_button = self.driver.find_element(By.CSS_SELECTOR, ".nearDistanceBox.active .npBtnBox button")
                            self.driver.execute_script("arguments[0].click();", view_less_button)
                            print("Clicked on View Less button.")
                            time.sleep(2)
                        except Exception as e:
                            print(f"Error clicking on View Less button: {e}")

                    except Exception as click_error:
                        print(f"Error clicking on landmark item: {click_error}")

                #print("Landmarks:", landmarks)
                # Convert landmarks list to a string format
                landmarks_text = "; ".join([f"{item['category']}: {', '.join([f'{detail['name']} ({detail['distance']})' for detail in item['details']])}" for item in landmarks]) if landmarks else "N/A"
                print("Landmarks:", landmarks_text)

            except Exception as e:
                print(f"An error occurred: {e}")
                landmarks_text = "N/A"
            try:
                # Locate the builder's total projects and experience
                total_projects_element = self.driver.find_element(By.XPATH, "//ul[@class='npTotalProjectList']/li[contains(text(), 'Total Projects')]/strong")
                total_projects = total_projects_element.text.strip()

            

                print("Total Projects:", total_projects)
            

            except Exception as e:
                total_projects = "N/A"
            
                print("Error extracting builder's total projects or experience:", e)

            try:
                # Wait until the "Configurations" section loads
                config = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//strong[text()='Configurations']/following-sibling::ol/li[1]/span"))
                )
                config=config.text.strip()

                print("Configurations:", config)  # Output: 2, 3 BHK Flats

            except Exception as e:
                config = "N/A"
                print("Error:", e)

            try:
                rera_panel = self.driver.find_element(By.CSS_SELECTOR, ".panelHeader[data-reraid]")
                
                rera_number = rera_panel.find_element(By.CSS_SELECTOR, "strong").text.split()[0].strip()
                    
                print("RERA Number:", rera_number)
            except Exception:
                rera_number = "N/A"
                print("RERA Number not found.")

            # Extract project status
            try:
                project_status_element = self.driver.find_element(By.CSS_SELECTOR, "td em.icon-project-status + span + strong")
                project_status = project_status_element.text.strip()
            except Exception:
                project_status = "N/A"
                print("Project Status not found.")

            video_count = 0
            try:
                badge_video_text = self.driver.find_element(By.CSS_SELECTOR, ".npFigure.video .badge").text
                if 'Video' in badge_video_text:
                    video_count = 1
                if '+' in badge_video_text and 'Video' in badge_video_text:
                    video_count = int(badge_video_text.split('+')[1].split()[0])
            except:
                pass  # no video badge


            csv_filename = "DataSquareyards.csv"
            file_exists = os.path.isfile(csv_filename)
            
            with open(csv_filename, "a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                if not file_exists or os.stat(csv_filename).st_size == 0:
                    writer.writerow([
                        "XID","URL", "Project Name","Builder Name", "Location", "Price Range", "Price per Sqft"
                        , "Configurations","Completion Date", "Unit Size Range","LandMarks","Project Size",
                        "Launch Date","RERA Number","Total Number of Units","USP","BHK" ,"Amenity Count"
                        ,"Amenities", "Specifications","Photo Count","Video Count","Rating count","Price Trend"
                        , "Builder URL", "Builder Experience","Total Projects",
                        "Ongoing Projects", "Past Projects","Builder Info","Project Status"
                    
                    ])
                writer.writerow([
                    xid,url, project_name,data_dict["Builder"], location, price_range, price_per_sqft,
                    config,data_dict["Completion Date"], data_dict["Unit Sizes"],landmarks_text,data_dict["Project Size"]
                    ,data_dict["Launch Date"],rera_number, data_dict["Total Number of Units"], usp,data_dict["Configurations"],amenity_count,amenities_text,specifications_text,image_count,video_count,
                    rating_count,price_trend,  data_dict["Builder URL"],
                    builder_experience,total_projects , ongoing_projects, past_projects,builder_info,project_status
                
                ])

            print(f"Data saved to {csv_filename}")

        except Exception as e:
            print(f"Error processing URL {url}: {e}")


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

    def unify(self, input_csv, outputData_csv, **kwargs):
        df = pd.read_csv(input_csv)
        column_map = {
            "magicbricks": "magicbricks.com link",
            "housing": "housing.com link",
            "squareyards": "squareyards.com link"
        }
        site_column = column_map[self.site]

        data = []

        for _, row in df.iterrows():
            xid = row['XID']
            url = row.get(site_column, None)
            if pd.notna(url):
                try:
                    print(f"Processing XID: {xid}, URL: {url}")
                    row_data = self.crawler.extract_project_data(xid, url, list(kwargs.keys()))
                    row_data['XID'] = xid
                    data.append(row_data)
                except Exception as e:
                    pass

        if data:
            output_df = pd.DataFrame(data)
            output_df.to_csv(outputData_csv, index=False)
            print(f"Saved output to {outputData_csv}")

        self.crawler.quit()


# Example usage:
# unifier = CrawlerUnifier("magicbricks")
# unifier.unify("projects.csv", "output_mb.csv", **{"Project Name": True, "Price Range": True, "Amenities": True})

# unifier2 = CrawlerUnifier("housing")
# unifier2.unify("projects.csv", "output_housing.csv", **{"Project Name": True, "Builder Name": True, "Avg Price psft": True})

# unifier3 = CrawlerUnifier("squareyards")
# unifier3.unify("projects.csv", "output_sy.csv", **{"Project Name": True, "Price per Sqft": True, "Amenities": True})

# unifier = CrawlerUnifier("magicbricks")
# unifier.unify("auditUrls.csv", "mb_data.csv", **{})

unifier2 = CrawlerUnifier("housing")
unifier2.unify("auditUrls.csv", "housing_data.csv", **{})

# unifier3 = CrawlerUnifier("squareyards")
# unifier3.unify("auditUrls.csv", "sy_data.csv", **{})