import pandas as pd

# Load CSV files
csv1 = pd.read_csv('csv1.csv')
csv2 = pd.read_csv('csv2.csv')

# Step 1: Filter csv1 where the link ends with '/project'
filtered_csv1 = csv1[csv1['Squareyards.com Link'].str.endswith('/project', na=False)]

# Step 2: Exclude XIDs that are present in csv2
xids_in_csv2 = set(csv2['XID'])
leftout = filtered_csv1[~filtered_csv1['XID'].isin(xids_in_csv2)]

# Step 3: Save to new CSV
leftout.to_csv('leftouturls.csv', index=False)
