if not floor_plans:
            #     try:
            #         print("hi")
            #         alternative_floor_plan_cards = driver.find_elements(By.CSS_SELECTOR, "div.pdp__prop__card")
            #         for card in alternative_floor_plan_cards:
            #             try:
            #                 # Extract unit type and size
            #                 unit_details = card.find_element(By.CSS_SELECTOR, "div.pdp__prop__card__bhk span").text.strip()
            #                 unit_type, unit_size = unit_details.split(" ", 1) if " " in unit_details else (unit_details, "Size Not Available")

            #                 # Extract price
            #                 try:
            #                     price = card.find_element(By.CLASS_NAME, "pdp__prop__card__price").text.strip()
            #                 except:
            #                     price = "Price Not Available"

            #                 # Extract possession date
            #                 try:
            #                     possession_date = card.find_element(By.CLASS_NAME, "pdp__prop__card__cons").text.strip()
            #                 except:
            #                     possession_date = "Possession Not Available"

            #                 # Append extracted details
            #                 floor_plans.append([xid,  unit_type, unit_size, "Area Not Available", price, possession_date])
            #             except Exception as e:
            #                 print(f"Skipping an alternative card due to error: {e}")
            #     except:
            #         print("No