import json
import os
import pandas as pd
from yfinance3 import YFinance3

# Read the CSV file and select columns 0 and 2
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])

# Filter out "Cash and/or Derivatives" sector
df = df[df.iloc[:, 1] != "Cash and/or Derivatives"]

# Extract the unique sectors from the selected columns
unique_sectors = df.iloc[:, 1].unique()

# Directory path to save JSON files
OUTPUT_DIRECTORY = 'json_list'

# Ensure the directory exists, create if not
os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

for sector in unique_sectors:
    selected_symbols = df[df.iloc[:, 1] == sector].iloc[:, 0].head(10).tolist()

    # Display the selected symbols
    print(f"Stock symbols in the {sector} sector:")
    print(selected_symbols[:10])  # Display the first 10 symbols
    selected_symbols = selected_symbols[:10]

    SYMBOLS = selected_symbols

    for symbol in SYMBOLS:
        file_name = os.path.join(OUTPUT_DIRECTORY, f'{symbol}.json')
        data = YFinance3(symbol)
        
        # Use a context manager to open the file and write the JSON data to it
        with open(file_name, 'w') as file:
            json.dump(data.info, file)
        
        print(f'Saved to {file_name}')
