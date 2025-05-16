import yfinance as yf
import schedule
import time
from datetime import datetime
from plyer import notification
import pygame
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

# Initialize pygame mixer
pygame.mixer.init()
sound = pygame.mixer.Sound("pop-1.mp3")

# List of companies with ticker symbols
companies = {
    "Bajaj Finance": "BAJFINANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "SBI": "SBIN.NS",
    "Muthoot Finance": "MUTHOOTFIN.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Infosys": "INFY.NS",
    "Reliance": "RELIANCE.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "TCS": "TCS.NS"
}

# Function to plot candlestick chart
def plot_candlestick(df, name):
    df.index = pd.DatetimeIndex(df.index)
    mpf.plot(df.tail(20), type='candle', style='charles', title=name, ylabel='Price')

# (Commented) Function to check if last 5 candles are bearish
# def check_bearish_candles(df):
#     last_5 = df.tail(5)
#     return all(candle['Open'] > candle['Close'] for _, candle in last_5.iterrows())

def check_conditions():
    print("🚀 Live Market Watch for 10 Companies...\n")
    for name, symbol in companies.items():
        data = yf.download(tickers=symbol, interval='1m', period='1d')

        if data.empty:
            print(f"⚠️ No data for {name}")
            continue

        latest = data.iloc[-1]
        open_price = latest['Open']
        high_price = latest['High']
        low_price = latest['Low']
        close_price = latest['Close']

        open_equal_low = open_price == low_price
        high_equal_close = high_price == close_price

        # Commented: Check for 5 bearish candles
        # bearish_candles = check_bearish_candles(data)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"🕒 {name} ({symbol}) - {now}")
        print(f"📊 OHLC - Open: {open_price:.2f}, High: {high_price:.2f}, Low: {low_price:.2f}, Close: {close_price:.2f}")

        print(f"📊 OHLC - Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}")
        print(f"🔍 Conditions: Open=Low? {open_equal_low}, High=Close? {high_equal_close}")
        print("-" * 40)

        # Alert only if Open == Low and High == Close
        if open_equal_low and high_equal_close:
            print("🚨 Alert: Open=Low and High=Close conditions matched!")
            notification.notify(
                title=f"{name} Alert",
                message="Open = Low & High = Close ✅",
                timeout=5
            )
            sound.play()
            plot_candlestick(data, name)

# Schedule the job every 5 minutes
schedule.every(5).minutes.do(check_conditions)

print("Starting scheduler... Press Ctrl+C to exit.")
while True:
    schedule.run_pending()
    time.sleep(1)
