import yfinance as yf
import pandas as pd

companies = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "State Bank of India": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Larsen & Toubro": "LT.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Axis Bank": "AXISBANK.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HCL Technologies": "HCLTECH.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Sun Pharmaceutical": "SUNPHARMA.NS",
    "Titan Company": "TITAN.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Mahindra & Mahindra": "M&M.NS",
    "Wipro": "WIPRO.NS",
    "Power Grid Corporation": "POWERGRID.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS"
}

# Define your condition checking function
def check_condition(df):
    # Example condition:
    # open == low and high == close for the candle
    # You can customize this function as per your exact logic
    
    # We'll check only last candle here, but you can loop through df as needed
    last_candle = df.iloc[-1]
    if last_candle['Open'] == last_candle['Low'] and last_candle['High'] == last_candle['Close']:
        return True
    return False

# Fetch and check each company
companies_meeting_condition = []

for name, ticker in companies.items():
    try:
        # Download 5min interval data for today
        data = yf.download(ticker, period="1d", interval="5m", progress=False)
        
        # Filter between 3:15 PM and 3:30 PM
        # data.index is a datetime index
        mask = (data.index.time >= pd.to_datetime("15:15").time()) & (data.index.time <= pd.to_datetime("15:30").time())
        timeframe_data = data.loc[mask]

        if timeframe_data.empty:
            # No data for that timeframe
            continue
        
        # Check your condition on this timeframe data
        # For example, check if any candle in this timeframe meets condition
        for i in range(len(timeframe_data)):
            candle = timeframe_data.iloc[i:i+1]
            if check_condition(candle):
                companies_meeting_condition.append(name)
                break

    except Exception as e:
        print(f"Error processing {name}: {e}")

print("Companies meeting condition between 3:15 PM and 3:30 PM:")
for c in companies_meeting_condition:
    print(c)
