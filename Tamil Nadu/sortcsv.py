import pandas as pd

# Load CSV file (Replace 'your_file.csv' with actual filename)
df = pd.read_csv("sorted_tobe.csv", dtype=str, header=None, names=["RegistrationNumber", "Year"])

# Normalize casing to avoid mismatches
df["RegistrationNumber"] = df["RegistrationNumber"].str.strip()

# Filter "Building" and "Layout" records
building_df = df[df["RegistrationNumber"].str.contains(r'/Building/', case=False, na=False)]
layout_df = df[df["RegistrationNumber"].str.contains(r'/Layout/', case=False, na=False)]

# Save to separate CSV files
building_df.to_csv("2025_building_data.csv", index=False)
layout_df.to_csv("2025_layout_data.csv", index=False)

# Print output to verify
print("Building Data:")
print(building_df)
print("\nLayout Data:")
print(layout_df)
