import yfinance as yf
import datetime
import time
import schedule
import pygame
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
from plyer import notification
import openpyxl
import os

# ========== Initialize pygame for sound ==========
pygame.init()
try:
    sound = pygame.mixer.Sound("pop-1.mp3")
except pygame.error:
    sound = None
    print("⚠️ Sound file not found or couldn't load.")

# ========== Excel setup ==========
excel_file = "alerts.xlsx"
if not os.path.exists(excel_file):
    wb = openpyxl.Workbook()
    wb.active.append(["Datetime", "Company", "Open", "High", "Low", "Close"])
    wb.save(excel_file)

# ========== Company Symbols ==========
companies = {
    "BAJFINANCE.NS": "Bajaj Finance",
    "HDFCBANK.NS": "HDFC Bank",
    "KOTAKBANK.NS": "Kotak Bank",
    "SBIN.NS": "SBI",
    "MUTHOOTFIN.NS": "Muthoot Finance",
    "TATAMOTORS.NS": "Tata Motors",
    "INFY.NS": "Infosys",
    "RELIANCE.NS": "Reliance",
    "ICICIBANK.NS": "ICICI Bank",
    "TCS.NS": "TCS"
}

# ========== Helper Functions ==========

def check_5_bearish(df):
    """Check if last 5 candles are bearish (Close < Open)."""
    if len(df) < 5:
        return False
    last_5 = df.tail(5)
    return all(float(row['Close']) < float(row['Open']) for _, row in last_5.iterrows())

def show_chart(df, symbol):
    """Display last 10 candles in chart."""
    mpf.plot(df.tail(10), type='candle', title=symbol, style='charles', volume=False)
    plt.show()

def log_to_excel(data):
    """Append alert data to Excel file."""
    try:
        wb = openpyxl.load_workbook(excel_file)
        ws = wb.active
        ws.append(data)
        wb.save(excel_file)
    except Exception as e:
        print(f"❌ Excel Logging Error: {e}")

def notify_user(title, message):
    """Trigger desktop notification."""
    notification.notify(
        title=title,
        message=message,
        app_name='Stock Alert',
        timeout=5
    )

# ========== Core Stock Checker ==========

def check_stocks():
    print("🚀 Live Market Watch for 10 Companies...\n")
    now = datetime.datetime.now()
    end_time = now
    start_time = now - datetime.timedelta(minutes=30)

    for symbol, name in companies.items():
        try:
            df = yf.download(
                tickers=symbol,
                interval="1m",
                start=start_time,
                end=end_time,
                progress=False,
                auto_adjust=False
            )

            if df.empty:
                print(f"⚠️ No data for {name} ({symbol})")
                continue

            # Flatten if multi-index
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            latest = df.iloc[-1]

            open_price = float(latest["Open"])
            high_price = float(latest["High"])
            low_price = float(latest["Low"])
            close_price = float(latest["Close"])

            datetime_str = latest.name.strftime('%Y-%m-%d %H:%M:%S') if isinstance(latest.name, pd.Timestamp) else str(latest.name)

            is_open_low = open_price == low_price
            is_high_close = high_price == close_price
            is_5_bearish = check_5_bearish(df)

            print(f"🕒 {name} ({symbol}) - {datetime_str}")
            print(f"📊 OHLC - Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}")
            print(f"🔍 Conditions: Open=Low? {is_open_low}, High=Close? {is_high_close}, 5 Bearish? {is_5_bearish}")

            if is_open_low and is_high_close and is_5_bearish:
                print(f"⚠️ Alert for {name} ({symbol})!")
                notify_user(f"Stock Alert: {name}", f"Open=Low, High=Close, 5 Bearish candles at {datetime_str}")
                if sound:
                    sound.play()
                log_to_excel([datetime_str, name, open_price, high_price, low_price, close_price])
                show_chart(df, name)

            print("-" * 40)

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

# ========== Scheduler ==========
def job():
    check_stocks()

if __name__ == "__main__":
    print("Starting scheduler... Press Ctrl+C to exit.")
    schedule.every(5).minutes.do(job)
    job()  # Run once immediately
    while True:
        schedule.run_pending()
        time.sleep(1)
