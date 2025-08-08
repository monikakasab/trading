import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, time
from bs4 import BeautifulSoup
from tabulate import tabulate
import mibian
import schedule
import time as t
import csv
import sys
import os
import constants 

# To run a job
def job():

    TOTAL_CE_COI = 0
    TOTAL_PE_COI = 0

    # Get option chain data
    data = get_option_chain_data()

    # Step 4: Find the specific strike price and print change in OIs
    for record in data['records']['data']:
        for STRIKE_PRICE in constants.STRIKE_PRICE_YOU_WANT:
            if record.get("expiryDate") == constants.EXPIRY and record.get("strikePrice") == STRIKE_PRICE:
                ce = record.get("CE", {})
                pe = record.get("PE", {})
                if ce:
                    TOTAL_CE_COI += ce['changeinOpenInterest']
                    #print(f"Strike: {STRIKE_PRICE} CE change in OI: {ce['changeinOpenInterest']}")
                if pe:
                    TOTAL_PE_COI += pe['changeinOpenInterest']
                    #print(f"Strike: {STRIKE_PRICE} PE change in OI: {pe['changeinOpenInterest']}")
                break

    #print(f"TOTAL_CE_COI: {TOTAL_CE_COI}")
    #print(f"TOTAL_PE_COI: {TOTAL_PE_COI}")
    TOTAL_COI = TOTAL_CE_COI + TOTAL_PE_COI
    #print(f"TOTAL_COI: {TOTAL_COI}")
    PCR = round((TOTAL_PE_COI / TOTAL_CE_COI), 2)
    CE_DIFF =(TOTAL_CE_COI/TOTAL_COI)*100
    PE_DIFF = (TOTAL_PE_COI/TOTAL_COI)*100
    PCR_DIFF = abs(PE_DIFF - CE_DIFF)
    #print(f"CE Difference: {CE_DIFF}")
    #print(f"PE Difference: {PE_DIFF}")
    #print(f"PCR Difference in %: {PCR_DIFF}")
    #print("===================")
    if PCR_DIFF < 20:
        DIFF_ANS = "YES"
    else:
        DIFF_ANS = "NO"

    def get_signal():
        if PE_DIFF > CE_DIFF:
            SIGNAL = "BUY CALL"
            return SIGNAL
        else:
            SIGNAL = "BUY PUT"
            return SIGNAL
        
    FINAL_SIGNAL = get_signal()
    #print(f"Signal : {FINAL_SIGNAL}")
    #print("===================")
    timestamp_str = datetime.now().strftime('%H:%M:%S')

    # Sample data to write

    headers = ['TIMESTAMP', 'TOTAL_CE_COI', 'TOTAL_PE_COI', 'TOTAL_COI', 'CE_RATIO', 'PE_RATIO', 'PCR DIFF', 'PCR', 'SIGNAL']
    data = [timestamp_str, TOTAL_CE_COI, TOTAL_PE_COI, TOTAL_COI, CE_DIFF, PE_DIFF, PCR_DIFF, PCR, FINAL_SIGNAL]
    
    directory = r'E:\Trading'

    # Ensure the directory exists, create if not
    os.makedirs(directory, exist_ok=True)

    # Base filename (without extension)
    filename = 'PCR_DATA'

    # Full path including directory and filename
    base_filename = os.path.join(directory, filename)

    # Function to create a filename with datetime suffix
    def create_timestamped_filename(base):
        now = datetime.now().strftime('%Y_%m_%d')
        return f"{base}_{now}.csv"

    # Find existing CSV files starting with base_filename
    os.chdir(directory)
    existing_files = [f for f in os.listdir('.') if f.startswith(filename) and f.endswith('.csv')]
    constants.FILENAME = create_timestamped_filename(filename)

    if not existing_files:
        # No file found, create new with datetime in name and write headers + data
        with open(constants.FILENAME, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)      # Write header
            writer.writerow(data)
        # print(f"CSV file created as '{constants.FILENAME}'")

    else:
        # Append data to the first found existing CSV file
        with open(constants.FILENAME, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
        # print(f"Data appended to existing file '{constants.FILENAME}'")

    print_data_on_console()
    
    #if DIFF_ANS == "YES":
    #    print("Wait for PCR DIFF to increase beyond 20% for greater accuracy")
        
def get_basic_info():
    print("\n")
    nifty = yf.Ticker('^NSEI')
    # Get daily bars - 'Open' for each trading day
    df = nifty.history(period='5d', interval='1d')

    # Get the open price for the most recent trading day (today if market has opened)
    todays_open = round(df.iloc[-1]['Open'])
    print("Nifty open price at 9:15AM:", todays_open)

    def round_to_nearest_strike(nifty_spot_price, step=50):
        return round(nifty_spot_price / step) * step

    nifty_spot_price = round_to_nearest_strike(todays_open)
    print(f"Nearest spot price: {nifty_spot_price}")

    # Get current date and time
    now = datetime.now()

    # Get the full weekday name (e.g., "Tuesday")
    constants.DAY  = now.strftime('%A')
    print(f"Today is: {constants.DAY}")

    def days_to_expire(day):
        match day:
            case "Monday":
                return 4
            case "Tuesday":
                return 3
            case "Wednesday":
                return 2
            case "Thursday":
                return 1
            case "Friday":
                return 5
            case _:
                return "Invalid day"
            
    # Get days remaning for the expiry
    days_to_expire = days_to_expire(constants.DAY)
    print(f"Days to expire: {days_to_expire}")

    start = nifty_spot_price             # NIFTY SPOT PRICE
    steps = days_to_expire               # How many steps to left and right
    step_size = 50                       # Step difference

    # Create list going left (decreasing)
    left_side = [start - step_size * i for i in range(steps, 0, -1)]

    # Current number itself
    center = [start]

    # Create list going right (increasing)
    right_side = [start + step_size * i for i in range(1, steps + 1)]

    # Combine all
    result = left_side + center + right_side

    constants.STRIKE_PRICE_YOU_WANT = result

    print(f"STRIKE_PRICE_YOU_WANT: {constants.STRIKE_PRICE_YOU_WANT}")

def get_option_chain_data():
    headers = {
        "user-agent": "Mozilla/5.0",
        "accept-language": "en-US,en;q=0.9"
    }
    session = requests.Session()

    # Step 1: Set cookies
    _ = session.get("https://www.nseindia.com/option-chain", headers=headers)

    # Step 2: Fetch option chain data
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={constants.UNDERLYING}"
    data = session.get(url, headers=headers).json()
    
    return data

def set_nearest_expiry(data):
    # Get the nearest expiry
    if constants.DAY == "Wednesday" or constants.DAY == "Thursday":
        constants.EXPIRY = data['records']['expiryDates'][1]
    else:
        constants.EXPIRY = data['records']['expiryDates'][0]
        
def print_expiry(expiry):
    print("===================")
    print(f"Expiry Selected: {expiry}")
    print("===================")
    
def print_data_on_console():
    if constants.HEADER_PRINTED is False:
        with open(constants.FILENAME, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)    # Read the header row
            data = list(reader)      # Read the data rows

        print(tabulate(data, headers=header, tablefmt='grid'))
        constants.HEADER_PRINTED = True
    else:    
        with open(constants.FILENAME, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)   # get the first row as header
            rows = list(reader)     # remaining rows as data
            new_row = rows[-1]  # Get last row (newly added line)
            # Print only the newly added line with headers shown once already
            print(tabulate([new_row], headers=[], tablefmt='grid'))  # No header repeat, simple line
        
exit_time = time(17, 30)  # 3:30 PM

# Run once immediately
get_basic_info()
data = get_option_chain_data()
set_nearest_expiry(data)
print_expiry(constants.EXPIRY)
job()


# Schedule the job every 3 inutes
schedule.every(3).minutes.do(job)

while True:
    now = datetime.now().time()
    if now >= exit_time:
        print("It's 3:30 PM or later. Exiting script.")
        sys.exit()
    schedule.run_pending()  # Run pending jobs
    t.sleep(1)
