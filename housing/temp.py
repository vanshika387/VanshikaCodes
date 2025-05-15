import pandas as pd

# Load the CSV files
print("Loading CSV files...")
csv1 = pd.read_csv("99acres.csv", encoding="ISO-8859-1")
csv2 = pd.read_csv("housing2.csv", encoding="ISO-8859-1")
print("CSV files loaded successfully.")

# Define column mapping between csv1 (99acres) and csv2 (housing)
column_mapping = {
    "name": "Name",
    "builderinfo_name": "Builder",
    "location_localityname": "Address",
    "constructionstage_constructionstatus": "Possession Status",
    "Registered": "RERA"
}

# Function to preprocess text
def preprocess(text):
    if pd.isna(text) or text == "nan":
        return ""
    return str(text).lower().replace("_", " ").strip()

# Function to match using in + token overlap
def is_match(val1, val2, threshold=0.7):
    if not val1 or not val2:
        return False

    if val1 in val2 or val2 in val1:
        return True

    tokens1 = set(val1.split())
    tokens2 = set(val2.split())
    overlap = tokens1 & tokens2

    similarity = len(overlap) / max(len(tokens1), len(tokens2))
    return similarity >= threshold

# Prepare lists to store matched and mismatched data
matches = []
mismatches = []

print("Starting the matching process...")

# Iterate over each row in housing.csv
for index, row in csv2.iterrows():
    xid = row["XID"]
    print(f"Processing XID: {xid} ({index + 1}/{len(csv2)})")
    match_row = csv1[csv1["XID"] == xid]

    if match_row.empty:
        print(f"XID {xid} not found in 99acres, skipping...")
        continue  # Skip if XID not found in 99acres

    match_row = match_row.iloc[0]  # Convert to series
    mismatch_entry = {"XID": xid}
    is_row_match = True

    for col1, col2 in column_mapping.items():
        val1 = preprocess(match_row[col1])
        val2 = preprocess(row[col2])

        # Special handling for RERA
        if col1 == "Registered":
            if val1 == "registered" and val2:
                score = 100
            elif val1 == "not registered" and ("not applicable" in val2 or val2 == ""):
                score = 100
            else:
                score = 0
        else:
            score = 100 if is_match(val1, val2) else 0

        print(f"Comparing {col2}: '{val1}' vs '{val2}', Score = {score}")
        mismatch_entry[col2] = row[col2] if score == 100 else f"99acres: {match_row[col1]} | Housing: {row[col2]}"
        mismatch_entry[f"{col2}_Score"] = score

        if score < 100:
            is_row_match = False

    if is_row_match:
        print(f"XID {xid} matched successfully.")
        matches.append(mismatch_entry)
    else:
        print(f"XID {xid} has mismatches.")
        mismatches.append(mismatch_entry)

print("Matching process completed.")

# Save results to CSV
print("Saving matches3.csv...")
pd.DataFrame(matches).to_csv("matches3.csv", index=False)
print("Saving mismatches3.csv...")
pd.DataFrame(mismatches).to_csv("mismatches3.csv", index=False)
print("Process completed successfully!")
