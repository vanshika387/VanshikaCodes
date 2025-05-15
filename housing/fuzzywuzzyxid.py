import pandas as pd
from fuzzywuzzy import process

# Load CSV files
csv1 = pd.read_csv("99acres.csv")
csv2 = pd.read_csv("housing.csv")

# Ensure column names are stripped of whitespace
csv1.columns = csv1.columns.str.strip()
csv2.columns = csv2.columns.str.strip()

# Lists to store results
results = []

# Iterate over each name in csv1
for index1, row1 in csv1.iterrows():
    xid = row1.get('XID', None)
    name1 = row1.get('name', '').strip()

    if not name1:  # Skip empty names
        continue

    # Find best match in csv2
    match = process.extractOne(name1, csv2['Name'].dropna(), score_cutoff=50)

    if match:
        best_match, best_score = match[:2]
        best_match_index = csv2[csv2['Name'] == best_match].index[0]
        serial_number = best_match_index + 1  # Assuming serial starts from 1
        results.append([xid, serial_number, best_score])
    else:
        results.append([xid, None, None])  # No match found

# Create DataFrame and save results
results_df = pd.DataFrame(results, columns=['XID', 'SerialNumber', 'Score'])
results_df.to_csv("matched_results.csv", index=False)

print("Matching completed. Results saved to matched_results.csv")
