import json
import os
import shutil
import pandas as pd
import schedule
import time
from yfinance3 import YFinance3

# Read the CSV file and select columns 0 and 2
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])

# Filter out "Cash and/or Derivatives" sector
df = df[df.iloc[:, 1] != "Cash and/or Derivatives"]

# Extract the unique sectors from the selected columns
unique_sectors = df.iloc[:, 1].unique()

# Directory path to save JSON files
OUTPUT_DIRECTORY = 'json_list'

# Function to delete JSON files
def delete_json_files():
    for filename in os.listdir(OUTPUT_DIRECTORY):
        file_path = os.path.join(OUTPUT_DIRECTORY, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

# Function to create JSON files
def create_json_files():
    for sector in unique_sectors:
        selected_symbols = df[df.iloc[:, 1] == sector].iloc[:, 0].head(10).tolist()
        for symbol in selected_symbols:
            file_name = os.path.join(OUTPUT_DIRECTORY, f'{symbol}.json')
            data = YFinance3(symbol)
            # Use a context manager to open the file and write the JSON data to it
            with open(file_name, 'w') as file:
                json.dump(data.info, file)
            print(f'Saved to {file_name}')

# Schedule deletion and creation of JSON files
schedule.every().tuesday.at("14:31").do(delete_json_files)
schedule.every().tuesday.at("14:32").do(create_json_files)

while True:
    schedule.run_pending()
    time.sleep(1)
