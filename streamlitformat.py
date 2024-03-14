import streamlit as st
import json
import os,shutil
from yfinance3 import YFinance3
# For DataFrame
import pandas as pd
import numpy as np
import datetime



# Main title on streamlit page
st.title('Fundamental Stock Analysis Tool')


# Reading Blackrock's İShares csv in order to identify the stocks and their industry/sector
df = pd.read_csv("iShares-Russell-3000-ETF_fund.csv", usecols=[0, 2])
unique_sectors = df.iloc[:, 1].unique()
unique_sectors = unique_sectors[unique_sectors != "Cash and/or Derivatives"]



# User preferred stocks
st.subheader("User Preferred Stocks (Enter multiple tickers separated by comma)")
user_input = st.text_input("Enter Stock Tickers")

# Extract individual stock tickers from the comma-separated input
user_stocks = [ticker.strip() for ticker in user_input.split(',') if ticker.strip()]

# Display the available sectors
with st.sidebar:
    st.subheader("Available Sectors")
    for i, sector in enumerate(unique_sectors, 1):
        
        st.write(f"{i}. {sector}")
            
            


# sector selection
number = st.number_input("Enter the index of the sector of interest: ", step=1, min_value=1, max_value=13)
selected_sector = unique_sectors[number - 1]

# defined symbols of stocks of the sector selection
selected_symbols = df[df.iloc[:, 1] == selected_sector].iloc[:, 0].head(10).tolist()

# displaying the results of the sector selection first the selected sector and the second list of the symbols of selected sector
st.write(f"Stock symbols in the {selected_sector} sector:")

with st.container():
    st.write(pd.DataFrame(selected_symbols[:10], columns=['Symbols']))

# Combine selected symbols and user-inputted symbols
symbols_list = list(set(selected_symbols + user_stocks))

if st.button("Selection", number):
    folder = 'json_list'
    sector_folder = os.path.join(folder, selected_sector)
        # Check if the user input symbols exist as JSON files
    for user_stock in user_stocks:
        user_stock_filename = os.path.join(folder, f'{user_stock}.json')
        if not os.path.exists(user_stock_filename):
            # Fetch data for the symbol
            data = YFinance3(user_stock)

            # Check if data is available
            if data.info is not None:
                # Write JSON data to file
                with open(user_stock_filename, 'w') as file:
                    json.dump(data.info, file)
                print(f"JSON data for symbol '{user_stock}' saved to '{user_stock_filename}'.")
                symbols_list.append(user_stock)
            else:
                st.write(f"No data available for symbol '{user_stock}'.")














######  CONFIGURATION  ########

# List of stock symbols we need to run fundamental analysis on - any symbol added here must have the json file
# containing stock info from YF
SYMBOLS = symbols_list
DATA_PATH = 'json_list'



# Dictionary to collect data to create a DF later
data = {
    'Symbol': [],
    'Name': [],
    'Industry': [],
    'EPS (fwd)': [],
    'P/E (fwd)': [],
    'PEG': [],
    'FCFY' : [],
    'PB': [],
    'ROE' : [],
    'P/S (trail)': [],
    'DPR' : [],
    'DY' : [],
    'CR' : [],
    'Beta': [],
    'Price': [],
    '52w Low': [],
    '52w High': [],
    'MarketCap': [],
    'Most Recent Quarter': [],

    }



######  LOADS DATA FROM JSON FILES  #######

def load_data(json_data):
    data['Symbol'].append(json_data.get('symbol', np.nan))
    data['Name'].append(json_data.get('longName', np.nan))
    data['Industry'].append(json_data.get('industry', np.nan))
    data['Price'].append(json_data.get('currentPrice', np.nan))
    data['MarketCap'].append(json_data.get('marketCap', np.nan))
    
    # Convert Most Recent Quarter timestamp to a date object
    most_recent_quarter = json_data.get('mostRecentQuarter', np.nan)
    if most_recent_quarter:
        most_recent_quarter_date = datetime.datetime.utcfromtimestamp(most_recent_quarter).date()
    else:
        most_recent_quarter_date = np.nan
    data['Most Recent Quarter'].append(most_recent_quarter_date)



    # Handle missing keys gracefully
    data['EPS (fwd)'].append(json_data.get('forwardEps', np.nan))
    data['P/E (fwd)'].append(json_data.get('forwardPE', np.nan))
    data['PEG'].append(json_data.get('pegRatio', np.nan))

    if 'freeCashflow' in json_data and 'marketCap' in json_data:
        fcfy = (json_data['freeCashflow'] / json_data['marketCap']) * 100
        data['FCFY'].append(round(fcfy, 2))
    else:
        data['FCFY'].append(np.nan)

    data['PB'].append(json_data.get('priceToBook', np.nan))
    data['ROE'].append(json_data.get('returnOnEquity', np.nan))
    data['P/S (trail)'].append(json_data.get('priceToSalesTrailing12Months', np.nan))

    data['DPR'].append(json_data.get('payoutRatio', np.nan) * 100)

    data['DY'].append(json_data.get('dividendYield', 0.0))
    data['Beta'].append(json_data.get('beta', np.nan))
    data['CR'].append(json_data.get('currentRatio', np.nan))

    data['52w Low'].append(json_data.get('fiftyTwoWeekLow', np.nan))
    data['52w High'].append(json_data.get('fiftyTwoWeekHigh', np.nan))



########  LOADS STOCK DATA FROM JSON FILES  ###########

for symbol in SYMBOLS:
    # Specify the full path to load JSON data
    file_name = f'{DATA_PATH}/{symbol}.json'    
    try:
        # Open the file in read mode
        with open(file_name, 'r') as file:
            # Use json.load() to parse the JSON data from the file
            load_data(json.load(file))
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")



########  CREATE DF  ###########

# Create a DF using the dictionary
df = pd.DataFrame(data)




# Add 52 week price range
df['52w Range'] = ((df['Price'] - df['52w Low'])/(df['52w High'] - df['52w Low']))*100



######  ADD STYLES TO DF  ######

def make_pretty(styler):
    # Column formatting
    styler.format({'EPS (fwd)': '${:.2f}', 'P/E (fwd)': '{:.2f}', 'PEG': '{:.2f}',
                   'FCFY': '{:.2f}%', 'PB' : '{:.2f}', 'ROE' : '{:.2f}', 'P/S (trail)': '{:.2f}',
                   'DPR': '{:.2f}%', 'DY': '{:.2f}%', 'CR' : '{:.2f}', 'Beta': '{:.2f}', '52w Low': '${:.2f}',
                   'Price': '${:.2f}', '52w High': '${:.2f}', '52w Range': '{:.2f}%','MarketCap': '${:,.0f}'
                  })

    # Set the bar visualization
    styler.bar(subset=['52w Range'], align="mid", color=["salmon", "cornflowerblue"])

    # Grid
    styler.set_properties(**{'border': '0.1px solid black'})

    # Set background gradients
    columns_to_gradient = ['EPS (fwd)', 'P/E (fwd)', 'PEG', 'FCFY', 'PB', 'ROE', 'P/S (trail)', 'DPR', 'DY', 'CR']
    for col in columns_to_gradient:
        styler.background_gradient(subset=[col], cmap='Greens')
    
    # No index
    styler.hide(axis='index')

    # Left text alignment for some columns
    styler.set_properties(subset=['Symbol', 'Name', 'Industry'], **{'text-align': 'left'})

    return styler


########  ADDS TOO TIPS ########
def populate_tt(df, tt_data, col_name):
    stats = df[col_name].describe()
    
    per25 = round(stats.loc['25%'], 2)
    per50 = round(stats.loc['50%'], 2)
    per75 = round(stats.loc['75%'], 2)

    # Get position based on the column name
    pos = df.columns.to_list().index(col_name)
    if col_name == 'MarketCap':
        stats = df[col_name].describe()
        for index, row in df.iterrows():
            mc = row[col_name]
            if mc == stats.loc['min']:
                tt_data[index][pos] = 'Lowest Market Cap'
            elif mc == stats.loc['max']:
                tt_data[index][pos] = 'Highest Market Cap'
            elif mc <= per25:
                tt_data[index][pos] = '25% of companies have Market Cap under {}'.format(per25)
            elif mc <= per50:
                tt_data[index][pos] = '50% of companies have Market Cap under {}'.format(per50)
            elif mc <= per75:
                tt_data[index][pos] = '75% of companies have Market Cap under {}'.format(per75)
            else:
                tt_data[index][pos] = '25% of companies have Market Cap over {}'.format(per75)
    else:
    
        for index, row in df.iterrows():
            pe = row[col_name]
            if pe == stats.loc['min']:
                tt_data[index][pos] = 'Lowest'
            elif pe == stats.loc['max']:
                tt_data[index][pos] = 'Hightest'
            elif pe <= per25:
                tt_data[index][pos] = '25% of companies under {}'.format(per25)
            elif pe <= per50:
                tt_data[index][pos] = '50% of companies under {}'.format(per50)
            elif pe <= per75:
                tt_data[index][pos] = '75% of companies under {}'.format(per75)
            else:
                tt_data[index][pos] = '25% of companies over {}'.format(per75)    



#######  APPLY STYLES AND TOOLTIPS ########

# Initialize tool tip data - each column is set to '' for each row
tt_data = [['' for x in range(len(df.columns))] for y in range(len(df))]

# Gather tool tip data for indicators
populate_tt(df, tt_data, 'EPS (fwd)')
populate_tt(df, tt_data, 'P/E (fwd)')
populate_tt(df, tt_data, 'PEG')
populate_tt(df, tt_data, 'FCFY')
populate_tt(df, tt_data, 'PB')
populate_tt(df, tt_data, 'ROE')
populate_tt(df, tt_data, 'P/S (trail)')
populate_tt(df, tt_data, 'DPR')
populate_tt(df, tt_data, 'DY')
populate_tt(df, tt_data, 'CR')
populate_tt(df, tt_data, 'MarketCap')

# Create a tool tip DF
ttips = pd.DataFrame(data=tt_data, columns=df.columns, index=df.index)

#Add table caption and styles to DF
df.style.pipe(make_pretty).set_caption('Fundamental Indicators').set_table_styles(
    [{'selector': 'th.col_heading', 'props': 'text-align: center'},
    {'selector': 'caption', 'props': [('text-align', 'center'),
                                       ('font-size', '11pt'), ('font-weight', 'bold')]}])
styled_df = df.style.pipe(make_pretty)
st.dataframe(styled_df)
