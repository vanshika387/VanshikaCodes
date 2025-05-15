import pandas as pd

# Load the CSV file
df = pd.read_csv('housing.csv', encoding='latin1')

# Add 'r' in front of each XID number
df['XID number'] = df['XID number'].apply(lambda x: f"r{x}")

# Save the updated CSV
df.to_csv('housing_updated.csv', index=False)

print("Updated CSV saved as 'housing_updated.csv'")
