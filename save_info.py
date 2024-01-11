from yfinance3 import YFinance3
import json
import os,shutil
import pandas as pd
import sys

#deleting all the existing files

folder = 'out/info'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))



# Read the CSV file and select columns 0 and 2
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])

# Extract the unique sectors from the selected columns
unique_sectors = df.iloc[:, 1].unique()

# Display the available sectors
print("Available sectors:")
for i, sector in enumerate(unique_sectors, 1):
    print(f"{i}. {sector}")

# Allow the user to select a sector
selected_sector_index = int(input("Enter the index of the sector of interest: "))
selected_sector = unique_sectors[selected_sector_index - 1]

# Filter symbols for the selected sector
selected_symbols = df[df.iloc[:, 1] == selected_sector].iloc[:, 0].head(10).tolist()

# Display the selected symbols
print(f"Stock symbols in the {selected_sector} sector:")
print(selected_symbols[:10])  # Display the first 10 symbols
selected_symbols=selected_symbols[:10]

SYMBOLS = selected_symbols

# Directory path to save JSON files
OUTPUT_DIRECTORY = 'out/info'

# Ensure the directory exists, create if not1

os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)


for symbol in SYMBOLS:
    file_name = os.path.join(OUTPUT_DIRECTORY, f'{symbol}.json')
    data = YFinance3(symbol)
    
    # Use a context manager to open the file and write the JSON data to it
    with open(file_name, 'w') as file:
        json.dump(data.info, file)
    
    print(f'Saved to {file_name}')
