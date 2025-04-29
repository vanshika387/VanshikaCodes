import requests
import pandas as pd
import time
import itertools
import random
import os
import csv
 
# Load API keys (Add at least 65 keys for 6,450 rows)
API_KEYS = [
    "AIzaSyBdousnphYiXq5PEfO4Rh5U5rP1vd_Z6QM",
    "AIzaSyD0md7Tvl7t0kNPL6vUuOPu1yLMFKgfPzM",
    "AIzaSyCt8Rd9E2mV03QGuvyvtu9Winv5xe3MFBA",
    "AIzaSyCy99elizENll8OuNiBtO-kwqD1DE0NKDo",
    "AIzaSyC541H8-ID9hY9EbxYHRhNuJRVt2718kuA",
    "AIzaSyDqPpCzCtcHZUuookA54-tSaLnRAtm6Jko",
    "AIzaSyA6RHbgSTw9OWJK16c6-wPEQOJfOvE9Bg8",
    "AIzaSyB7GhiFMP7_maGcKxVnpTAvKkt9FlkcIGw",
    "AIzaSyD4aPVW68snVLIvMvddwLhuOmBU2w8tHS8",
    "AIzaSyA_euod8-z8jX4yEk-edLLNOQs8-a9IQ4A",

    "AIzaSyCnak7cLRkU0ZzAsf8Dd1Ao6Mf7Pei-Qzk",
    "AIzaSyAOCJpr5K9OcaJMNXZ_BWT4dfaLtjwszsg",
    "AIzaSyDbGb5ZnAl4bNQArfWNVCT_xCYTcZcEcrA",
    "AIzaSyBQs3uf9Tdn8WDSmJ_kD5tdDgb0MkxxllY",
    "AIzaSyCR7Nr3WvNiQ2O1DfRMfvtmR_3U-qPOqWg",
    "AIzaSyBwKQjyB_XSuLb5iZkZzmU68DLOG3W6N-A",
    "AIzaSyDjVcRtCSaRp_0eaBh5wmpyupIZe5QXmoU",
    "AIzaSyAPb3jLj4fq2Bd3_qoDc-VruwzA237v3cA",
    "AIzaSyAbiRQC5mIkc7YVEfigATUue6HGvpY6gjM", 
    "AIzaSyC53ROiYRQc9YC06W4sZxIYKraBno9Z-m0",
    "AIzaSyDrYC-ou_j4jkTIjlp948y50eUKssBx32s",
    "AIzaSyB9clIT5p171JugNT0AHf9PgWaz2AdaLKY",
    "AIzaSyCZER2okoZQKAsTxdHFDB43jhQ3Jgryl3c",
    "AIzaSyCk86WnVeI_JKQeFfSE0dMZ49qvQbauMtU",
    "AIzaSyCA2F423V-hH1C83ZFoi7lYu7qtsZolQns",
    "AIzaSyCatk1pZs6BYjzxBjD2V3rvhAFs6xu1zHM",
    "AIzaSyCclCkgA6m9lDm5gGjLnhXWfGVbiAbgaUc" ,

    "AIzaSyDJlXCzsYB9M-C5RtlitUG8BbsMkdnoyfM",
    "AIzaSyDoUKeaDU92zQ35q2AAjxAjaNlmW2RJxxU",
    "AIzaSyAtZLBhYRRcpJ-0p3UOg9eevZzI-cK35Pg",
    "AIzaSyDsksKYko-M22U-N-lzKu8KCAxG6z6fOc0",
    "AIzaSyDnwYFzdVF5pZBK9WIlPcvgKvxkt0Faftw",
    "AIzaSyCSISKrI4YH5Hp0c80dIc5UG-jYgHg7G50",
    "AIzaSyAAdVEca1YgM2HUI7wKOZSNn4zoCMi5myQ",
    "AIzaSyDdjra19w3MtbOll8Mbpig9Qt4WMNUANzQ",
    "AIzaSyDgS-vrMcMsKs-iyX9vBPFNUgP12HiKmeI",
    "AIzaSyC_LoHo5-iYOJPkTj4aP6oeW0yOQysYmRU",
    "AIzaSyBYwWVzNOHNwObPV4Xxw-s_AzyiLnQ_sfI",
    "AIzaSyClwJv_6EIHOxWzkdI8v57aWBA1iTQ6DnY",
    "AIzaSyD8h-ZXU8-tbwNT2qgKeUkVJ-ylMAPpYNA",
    "AIzaSyAkyK9-M8IcD2OZSSBovhSWnIRWDt95sDo",
    "AIzaSyBD9TKn2UrNSej4CwCWsdxgFWTN0mSFHmo",
    "AIzaSyC9AX7hmJl-6ZjPiRrIbLT-7WRfiQ6xiFE",
    "AIzaSyAsyKg1Qkt2pll1Uok6ZJHjZzx2TUhgazM",
    "AIzaSyB2luEX9qNGWlp5pLxFkzuJzfZb3dFbvTQ"

    # "AIzaSyDwMb4McmDsQqD3VdZm4_25k16cyDf_bqU",
    # "AIzaSyCRARYzF_OPiGKVadN9uPDIzvzeoVLmr6M",
    # "AIzaSyDG6uXImnyUY-MdYdBlbyeuwN0QQXhRrxk",
    # "AIzaSyDLKYpQtaELXowh7F_zEDLQiuSuMegjlC4",
    # "AIzaSyCW73HKSwwr34c6vYsQIdqIr3ppZ8VH19M",
    # "AIzaSyBx__gjAKpp5S2ynCPhtFbNSTGGDuUE2Fs",
    # "AIzaSyD0IlWMTPZ1gEcFd7e4_aWKOyD_kX86Ew4",
    # "AIzaSyBSxhkljCL3bNrbb9Kd86WAjA6yWRZt6g0",
    # "AIzaSyCz6kAtWobsEhNUggj2-0j9vlBXt2CbHZg",
    # "AIzaSyD4tj72-pQ83P62mcEYZ3C1jGR1vztQK4Y",
    # "AIzaSyBnf_PsKHV9fT3tIhoBNOE5gmkQOdjnfFc",
    # "AIzaSyD_p3nmMAi5wl2g3JGFaQI2bwoD2XqRQuE", 
    # "AIzaSyBGR3MkOTyTmuv2SYLbaQrL6cQd1eOncpo",
    # "AIzaSyBCxlOa4Ux5qqfSBl9lUj1MN-nVRCc2eJI",
    # "AIzaSyC6BdfG72p7omdPNbpm1giH8ftJnDH2BxI",
    # "AIzaSyAbl_p9xXpSi7l18uJlXfp0hbKI5b7gShc",
    # "AIzaSyBxW4git9JrjeNy64GWlerPQ0vkKVv3BQg",
    # "AIzaSyChBlQqU63f5URh5Sv-gtxqyQzqobb2xn0",
    # "AIzaSyB_TV2o3o0IFaPBKMc4IDGTA6Z33ZHj17I",
    # "AIzaSyBWvXQhei6McayXXNR9WZ6yNqet_G2Czfo",
    # "AIzaSyAxvK1ZWibBgeos3hol4AWzTq_UM31C0xE",
    # "AIzaSyD0MsRY2edpGMY7xQszDZqs8WB9vC3C-sA",
    # "AIzaSyCtQkAuGbpEVvqXe9MaXQJ-hi_QZiHDLic",
    # "AIzaSyBH9rUTw3MchknfdDM4P4OW4C4yCzTCe6k",
    # "AIzaSyAQkLZ2kQMD4F2_1Hu7hEXCghyUz2MrRCg",
    # "AIzaSyBogpNygc1Zk4XOX-BYw7ljOyi_T55qU5I",
    # "AIzaSyCdBZ8sKeL1DblLhSCAhUrBDlkLOHV9zWk",
    # "AIzaSyBl54WXS_Kr2SKyd33o_CwDHtkW0QyHD5k",
    # "AIzaSyAWfoEl_sP-WByz8UO_l3KH9Xtp2Zt5VfM",
    # "AIzaSyBlfoYRAZLNLAk_BZ9xcxd5zY0hWVHvjvU",
    # "AIzaSyA_LXGhOr0GkEr1lOo8_GDd1bJ11IMPQZ4",
    # "AIzaSyC8cEsYc-DbS_wIGaZkRYF6pqDvGdsQTpU",
    # "AIzaSyCi4cjHYtpKg_VKU7xzHo2NWy5K0Sp0vro",
    # "AIzaSyBofHbqK3HwzaOAtD_Er3B9ZDDDgHzyx9Y",
    # "AIzaSyCOsvnE8BTXPb34-gIRa-rbdSetVSEYLF8",
    # "AIzaSyBNMVDiYFQHumbDnysNcnRadHmLXbTlatw",
    # "AIzaSyBDlVWZ2gAxGbWDXoDb1v7CrmBlXVmsiew",
    # "AIzaSyB3Lbb6pvwVIe__OhWvS8l8ddpYhVTGpaA"
 
 
 
 
]
 
CX = "85dfa13c72e034042"  # Custom Search Engine ID
 
# API Usage Tracking
api_usage_count = {key: 0 for key in API_KEYS}
api_cycle = itertools.cycle(API_KEYS)  # Round-robin cycle
 
# Settings for rate limiting
API_SWITCH_TIME = random.uniform(6, 8)  # Switch API keys every 6-8 seconds
MAX_REQUESTS_PER_MINUTE = 50  # Keep below 100 to avoid bans
REQUEST_DELAY = random.uniform(2.5, 3)  # Delay between requests (1.5 - 2s)
 
last_switch_time = time.time()
 
# Check if an output file exists and resume processing
output_file = "outputUrls3.csv"
if os.path.exists(output_file):
    existing_df = pd.read_csv(output_file)
    processed_xids = set(existing_df["XID"].astype(str))
else:
    processed_xids = set()
 
def get_next_api_key():
    """Returns the next valid API key, ensuring it has not exceeded 100 requests."""
    global last_switch_time
    current_time = time.time()
 
    # Switch API key if time limit reached (6-8 seconds)
    if current_time - last_switch_time > API_SWITCH_TIME:
        while True:
            api_key = next(api_cycle)
            if api_usage_count[api_key] < 90:
                last_switch_time = time.time()  # Update switch time
                return api_key
    else:
        return next(api_cycle)  # Continue using current API key
 
# Load Excel file
file_path = r"newList.xlsx"
df = pd.read_excel(file_path)
 
# Ensure column names are correct
if 'proj_name' not in df.columns or 'City' not in df.columns or 'XID' not in df.columns:
    raise ValueError("Excel file must contain 'proj_name', 'City', and 'XID' columns")
 
df = df[df["XID"].astype(str).isin(processed_xids) == False]  # Skip already processed rows
df = df.iloc[:3200]
 
output_data = []
current_api_key = get_next_api_key()  # Get first valid API key
 
# Process rows
for index, row in df.iterrows():
    time.sleep(REQUEST_DELAY)  # Add delay to prevent hitting rate limits
 
    xid = str(row["XID"]).strip()
    proj_name = str(row["proj_name"]).strip()
    City = str(row["City"]).strip()
    query = f"{proj_name} {City} squareyards.com"
 
    # Get a valid API key based on time interval and usage count
    current_api_key = get_next_api_key()
    api_usage_count[current_api_key] += 1  # Increment usage count
 
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={current_api_key}&cx={CX}"
    response = requests.get(url)
    data = response.json()
 
    # If Google blocks due to rate limits, wait before retrying
    if "error" in data and data["error"]["code"] == 429:
        print(f"Rate limit exceeded for {current_api_key}, switching key...")
        time.sleep(8)  # Wait before switching keys
        current_api_key = get_next_api_key()  # Get a new key
        continue  # Retry the request
 
    magic_link = "Not Found"
    if "items" in data:
        for item in data["items"]:
            if "squareyards.com" in item["link"] :
                magic_link = item["link"]
                break  # Stop once we find the first magicbricks.com link with pdpid
 
    print(f"Row {index+1}: XID:{xid}, Project: {proj_name}, City: {City}, Link: {magic_link}, API Used: {current_api_key}")
 
    # Append data to CSV file immediately
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if f.tell() == 0:  # Check if file is empty to write header
            writer.writerow(["XID", "Project Name", "City", "Squareyards.com Link"])
        writer.writerow([xid, proj_name, City, magic_link])
 
   
    # If we are close to exceeding the per-minute limit, slow down
    if (index + 1) % MAX_REQUESTS_PER_MINUTE == 0:
        print(f"Reached {MAX_REQUESTS_PER_MINUTE} requests, pausing for a while...")
        time.sleep(30)  # Cooldown before resuming
 
# # Final save
# output_df = pd.DataFrame(output_data, columns=["XID", "Project Name", "City", "Magicbricks.com Link"])
# if os.path.exists(output_file):
#     output_df.to_csv(output_file, index=False, mode='a', header=False)
# else:
#     output_df.to_csv(output_file, index=False)
 
print("Results saved to 'Squareyards.com_links.csv'.")
 
 