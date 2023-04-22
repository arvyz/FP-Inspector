import json
import pandas as pd
import openpyxl

# Load the JSON file
with open('fingerprinting_domains.json') as f:
    data = json.load(f)

# Create an empty list to hold the data items
items = []

# Loop through each item in the data dictionary
for key, values in data.items():
    # Loop through each value in the list of values
    for value in values:
        # Append a dictionary with the desired values to the items list
        items.append({
            'top_url': value['top_url'],
            'script_url': value['script_url']
        })

# Create a DataFrame from the items list
df = pd.DataFrame(items)

# Write the DataFrame to an Excel file
df.to_excel('fpdomains.xlsx', index=False)


