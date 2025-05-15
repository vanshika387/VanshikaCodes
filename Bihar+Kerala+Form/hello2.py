import pandas as pd

# df = pd.read_csv('data3.csv')

# print(df.to_string()) 

# df.to_csv('output.csv', index=False)
import csv
data = [['Name', 'Age', 'City'],
        ['Alice', 25, 'New York'],
        ['Bob', 30, 'Los Angeles'],
        ['Charlie', 35, 'Chicago']]
 
# Writing to a CSV file
with open('data2.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)