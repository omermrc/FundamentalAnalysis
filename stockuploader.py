import json
import os
from yfinance3 import YFinance3
import pandas as pd

# Reading Blackrock's İShares csv in order to identify the stocks and their industry/sector
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])

# Create a folder to store JSON files if it doesn't exist
os.makedirs('json_list', exist_ok=True)

# Iterate over all symbols in the DataFrame
for symbol, sector in zip(df.iloc[:, 0], df.iloc[:, 1]):
    # Skip symbols categorized as "Cash and/or Derivatives"
    if sector == "Cash and/or Derivatives":
        print(f"Skipping symbol '{symbol}' categorized as 'Cash and/or Derivatives'.")
        continue
    
    # Construct the file name for the JSON file
    file_name = os.path.join('json_list', f'{symbol}.json')

    # Check if the file already exists
    if os.path.exists(file_name):
        print(f"File '{file_name}' already exists. Skipping.")
        continue

    # Download JSON data for the symbol
    data = YFinance3(symbol)

    # Check if data is available
    if data.info is None:
        print(f"No data available for symbol '{symbol}'.")
        continue

    # Use a context manager to open the file and write the JSON data to it
    with open(file_name, 'w') as file:
        json.dump(data.info, file)

    print(f"JSON data for symbol '{symbol}' saved to '{file_name}'.")
