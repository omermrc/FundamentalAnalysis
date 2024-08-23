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

def create_json_files():
    for sector in unique_sectors:
        # Gather initial symbols to process
        sector_df = df[df.iloc[:, 1] == sector]
        selected_symbols = sector_df.iloc[:, 0].tolist()
        
        successful_symbols = []
        failed_symbols = []
        all_symbols = set(selected_symbols)
        
        # Process up to 10 symbols
        while len(successful_symbols) < 10 and selected_symbols:
            symbol = selected_symbols.pop(0)  # Get the next symbol
            file_name = os.path.join(OUTPUT_DIRECTORY, f'{symbol}.json')
            try:
                data = YFinance3(symbol)
                info = data.info  # Access info as a property, not a method
                if isinstance(info, dict):  # Check if info is a dictionary
                    with open(file_name, 'w') as file:
                        json.dump(info, file)
                    print(f'Saved to {file_name}')
                    successful_symbols.append(symbol)
                else:
                    print(f"No data available for symbol {symbol}")
                    failed_symbols.append(symbol)
            except Exception as e:
                print(f"Error processing symbol {symbol}: {e}")
                failed_symbols.append(symbol)
        
        # If fewer than 10 successful symbols, replace failed ones
        if len(successful_symbols) < 10:
            remaining_needed = 10 - len(successful_symbols)
            additional_symbols = [s for s in all_symbols if s not in successful_symbols and s not in failed_symbols]
            
            # Re-attempt with remaining symbols if needed
            while remaining_needed > 0 and additional_symbols:
                symbol = additional_symbols.pop(0)
                file_name = os.path.join(OUTPUT_DIRECTORY, f'{symbol}.json')
                try:
                    data = YFinance3(symbol)
                    info = data.info
                    if isinstance(info, dict):
                        with open(file_name, 'w') as file:
                            json.dump(info, file)
                        print(f'Saved to {file_name}')
                        successful_symbols.append(symbol)
                        remaining_needed -= 1
                except Exception as e:
                    print(f"Error processing symbol {symbol}: {e}")

        if len(successful_symbols) < 10:
            print(f"Only {len(successful_symbols)} symbols processed for sector {sector}.")
        else:
            print(f"Successfully processed 10 symbols for sector {sector}.")
delete_json_files()
create_json_files()
# Schedule deletion and creation of JSON files
schedule.every().friday.at("15:48").do(delete_json_files)
schedule.every().friday.at("14:49").do(create_json_files)

while True:
    schedule.run_pending()
    time.sleep(1)
