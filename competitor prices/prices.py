import pandas as pd

# Use latin1 to handle weird characters
housing_df = pd.read_csv("housing.csv", encoding='latin1')
magicbricks_df = pd.read_csv("magicbricks.csv", encoding='latin1')
squareyards_df = pd.read_csv("squareyards.csv", encoding='latin1')

# Extract and rename
housing_prices = housing_df[['XID number', 'Price Range']].rename(columns={
    'XID number': 'XID',
    'Price Range': 'Housing Price Range'
})
magicbricks_prices = magicbricks_df[['XID', 'Price']].rename(columns={
    'Price': 'MagicBricks Price'
})
squareyards_prices = squareyards_df[['XID', 'Price Range']].rename(columns={
    'Price Range': 'SquareYards Price Range'
})

# Ensure XID is string in all
housing_prices['XID'] = housing_prices['XID'].astype(str)
magicbricks_prices['XID'] = magicbricks_prices['XID'].astype(str)
squareyards_prices['XID'] = squareyards_prices['XID'].astype(str)

# Merge
merged = pd.merge(housing_prices, magicbricks_prices, on='XID', how='outer')
merged = pd.merge(merged, squareyards_prices, on='XID', how='outer')

# Fill and save
merged.fillna("Not Found", inplace=True)
merged.sort_values(by='XID', inplace=True)
merged.to_csv("merged_prices.csv", index=False)

print("✅ Done! 'merged_prices.csv' created.")
