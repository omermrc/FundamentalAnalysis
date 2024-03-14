import json
import os,shutil
import pandas as pd
from yfinance3 import YFinance3
import schedule
# Read the CSV file and select columns 0 and 2
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])

# Filter out "Cash and/or Derivatives" sector
df = df[df.iloc[:, 1] != "Cash and/or Derivatives"]

# Extract the unique sectors from the selected columns
unique_sectors = df.iloc[:, 1].unique()

# Directory path to save JSON files
OUTPUT_DIRECTORY = 'json_list'

for filename in os.listdir(OUTPUT_DIRECTORY):
    file_path = os.path.join(OUTPUT_DIRECTORY, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))




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
