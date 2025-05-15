# import pandas as pd

# # Load both CSV files
# file_99acres = "99acres.csv"
# file_housing = "housing.csv"

# df_99acres = pd.read_csv(file_99acres)
# df_housing = pd.read_csv(file_housing)

# # Merge on XID
# df_merged = pd.merge(df_99acres, df_housing, on='XID', suffixes=('_99acres', '_housing'))

# # Define common attributes with potential different names
# attribute_mapping = {
#     'name': 'Name',
#     'builderinfo_name': 'Builder',
#     'location_localityname': 'Address',
#     'constructionstage_completiondate_numberlong': 'Possession Starts',
#     'Registered': 'RERA'
# }

# # Store mismatches and matches
# mismatches = []
# matches = []

# # Iterate over merged rows to compare values
# for _, row in df_merged.iterrows():
#     mismatch_entry = {'XID': row['XID']}
#     match_entry = {'XID': row['XID']}
    
#     for col_99acres, col_housing in attribute_mapping.items():
#         if col_99acres in df_99acres.columns and col_housing in df_housing.columns:
#             value_99acres = str(row[col_99acres]).strip().lower()
#             value_housing = str(row[col_housing]).strip().lower()
            
#             if value_99acres != value_housing:
#                 mismatch_entry[col_99acres] = f"99acres: {row[col_99acres]} | Housing: {row[col_housing]}"
#             else:
#                 match_entry[col_99acres] = row[col_99acres]
    
#     if len(mismatch_entry) > 1:
#         mismatches.append(mismatch_entry)
#     if len(match_entry) > 1:
#         matches.append(match_entry)

# # Save mismatches to a new CSV
# if mismatches:
#     df_mismatches = pd.DataFrame(mismatches)
#     df_mismatches.to_csv("mismatches.csv", index=False)
#     print("Mismatches saved to mismatches.csv")
# else:
#     print("No mismatches found!")

# # Save matches to a new CSV
# if matches:
#     df_matches = pd.DataFrame(matches)
#     df_matches.to_csv("matches.csv", index=False)
#     print("Matches saved to matches.csv")
# else:
#     print("No matches found!")

import pandas as pd

# Load both CSV files
file_99acres = "99acres.csv"
file_housing = "housing.csv"

df_99acres = pd.read_csv(file_99acres)
df_housing = pd.read_csv(file_housing)

# Merge on XID
df_merged = pd.merge(df_99acres, df_housing, on='XID', suffixes=('_99acres', '_housing'))

# Define common attributes with potential different names
attribute_mapping = {
    'name': 'Name',
    'builderinfo_name': 'Builder',
    'location_localityname': 'Address',
    'constructionstage_completiondate_numberlong': 'Possession Starts',
    'Registered': 'RERA'
}

# Store mismatches and matches
mismatches = []
matches = []

# Iterate over merged rows to compare values
for _, row in df_merged.iterrows():
    mismatch_entry = {'XID': row['XID']}
    is_mismatch = False
    common_name = row['name'] if 'name' in df_99acres.columns else row['Name']
    mismatch_entry['Name'] = common_name  # Ensure name is always included
    
    for col_99acres, col_housing in attribute_mapping.items():
        if col_99acres in df_99acres.columns and col_housing in df_housing.columns:
            value_99acres = str(row[col_99acres]).strip().lower()
            value_housing = str(row[col_housing]).strip().lower()
            
            if value_99acres != value_housing:
                mismatch_entry[col_99acres] = f"99acres: {row[col_99acres]} | Housing: {row[col_housing]}"
                is_mismatch = True
    
    if is_mismatch:
        mismatches.append(mismatch_entry)
    else:
        matches.append(row.to_dict())

# Save mismatches to a new CSV
if mismatches:
    df_mismatches = pd.DataFrame(mismatches)
    df_mismatches.to_csv("mismatches.csv", index=False)
    print("Mismatches saved to mismatches.csv")
else:
    print("No mismatches found!")

# Save matches to a new CSV
if matches:
    df_matches = pd.DataFrame(matches)
    df_matches.to_csv("matches.csv", index=False)
    print("Matches saved to matches.csv")
else:
    print("No matches found!")
