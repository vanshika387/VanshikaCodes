import pandas as pd
import re
import Levenshtein

# Load CSV files with encoding
csv1 = pd.read_csv("regData.csv", encoding="utf-8")
csv2 = pd.read_csv("template.csv", encoding="utf-8")

# Normalize column names to avoid KeyErrors
csv1.columns = csv1.columns.str.strip().str.lower()
csv2.columns = csv2.columns.str.strip().str.lower()

# Check if required columns exist
required_columns = {"state", "unmatched_registration_number"}
if not required_columns.issubset(csv1.columns):
    missing = required_columns - set(csv1.columns)
    raise KeyError(f"Missing required columns in regData.csv: {missing}")

# Identify pattern columns in template.csv
pattern_columns = [col for col in csv2.columns if col.startswith("pattern ex.-")]

# Lists to store matched and unmatched registration numbers
matched_numbers = []
unmatched_numbers = []

# Function to convert pattern into regex while preserving spaces and ignoring case
def convert_to_regex(pattern):
    pattern = pattern.strip()
    
    # Only replace numeric literals, avoiding already escaped \d
    pattern = re.sub(r'(?<!\\)(\d+)', r'\\d+', pattern)  

    # Convert spaces into flexible matching (\s+)
    pattern = re.sub(r'(?<!\\)\s+', r'\\s+', pattern)

    # Handle parentheses safely
    pattern = pattern.replace("(", r"\(\s*").replace(")", r"\s*\)")

    return f'(?i)^{pattern}$'  # Ensure full match, ignore case

# Iterate through csv1
for index, row in csv1.iterrows():
    state = row["state"].strip()
    registration_number = str(row["unmatched_registration_number"]).strip()
    
    # Find the matching state in csv2
    state_data = csv2[csv2["state"].str.strip() == state]
    if state_data.empty:
        unmatched_numbers.append([state, registration_number, "No Match"])
        continue
    
    state_patterns = state_data[pattern_columns].values.flatten()
    state_patterns = [str(p).strip() for p in state_patterns if pd.notna(p)]
    regex_patterns = [convert_to_regex(p) for p in state_patterns]

    # Check if registration number matches any pattern
    if any(re.fullmatch(pattern, registration_number, re.IGNORECASE) for pattern in regex_patterns):
        matched_numbers.append([state, registration_number])
    else:
        # Find the closest template using Levenshtein Distance
        closest_match = min(state_patterns, key=lambda p: Levenshtein.distance(p, registration_number))
        unmatched_numbers.append([state, registration_number, closest_match])

# Save matched registration numbers to a new CSV
matched_df = pd.DataFrame(matched_numbers, columns=["state", "matched_registration_number"])
matched_df.to_csv("matched_numbers3.csv", index=False, encoding="utf-8")

# Save unmatched registration numbers with closest match to a new CSV
unmatched_df = pd.DataFrame(unmatched_numbers, columns=["state", "unmatched_registration_number", "closest_template_match"])
unmatched_df.to_csv("unmatched_numbers3.csv", index=False, encoding="utf-8")

print("Script executed successfully. Matched registration numbers saved in 'matched_numbers2.csv'.")
print("Unmatched registration numbers (with closest match) saved in 'unmatched_numbers2.csv'.")
