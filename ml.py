import yfinance as yf
import schedule
import time
from datetime import datetime
import pygame
import pandas as pd
import mplfinance as mpf
from plyer import notification
import openpyxl
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialize pygame mixer for sound alerts
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("pop-1.mp3")

# Excel logging
excel_file = "matched_conditions.xlsx"
try:
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active
except FileNotFoundError:
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Company", "Date", "Open", "High", "Low", "Close", "Condition", "ML_Prediction"])

# Stock watchlist
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


# Email config
EMAIL_ADDRESS = "shaguftafatima444@gmail.com"
EMAIL_PASSWORD = "nkaz nrou yugv tavu"
# EMAIL_RECEIVER = "koolifashion123@gmail.com"
EMAIL_RECEIVER ="shaguftafatma861@gmail.com"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def train_model(df):
    df = df.copy()
    df['Target'] = (df['Close'].shift(-1) > df['Open'].shift(-1)).astype(int)
    df.dropna(inplace=True)
    X = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    y = df['Target']
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model

def predict_bullish(model, row):
    X_pred = row[['Open', 'High', 'Low', 'Close', 'Volume']].values.reshape(1, -1)
    return model.predict(X_pred)[0]

def plot_candlestick(data, ticker):
    df = data.copy()

    # Flatten MultiIndex columns
    df.columns = [f"{col[0]}_{col[1]}" for col in df.columns]

    # Extract specific company data
    df = df[[f'Open_{ticker}', f'High_{ticker}', f'Low_{ticker}', f'Close_{ticker}']]
    df.columns = ['Open', 'High', 'Low', 'Close']

    # Convert to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df.dropna(inplace=True)

    # Plot using mplfinance or matplotlib
    # import mplfinance as mpf
    mpf.plot(df, type='candle', style='charles', title=f'{ticker} Candlestick', ylabel='Price')

    print(f"Type of df: {type(df)}")
    print(f"Columns in df: {df.columns if hasattr(df, 'columns') else 'No columns attribute'}")
    
    for col in ['Open', 'High', 'Low', 'Close']:
        if col not in df.columns:
            print(f"Column {col} not found in DataFrame!")
            return
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
    
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    
    df = df.sort_index()

    if df.empty:
        print("DataFrame is empty after dropping NaNs. Cannot plot.")
        return

    mpf.plot(df, type='candle', style='charles', title=name, ylabel='Price')


# Main function
def check_conditions():
    for name, symbol in companies.items():
        data = yf.download(symbol, period="2d", interval="5m", auto_adjust=True)
        if data.empty or len(data) < 10:
            print(f"❌ Not enough data for {name}")
            continue

        model = train_model(data.copy())
        row = data.iloc[-1]
        open_price =float(row['Open'].iloc[0])
        high_price =  float(row['High'].iloc[0])
        low_price = float(row['Low'].iloc[0])
        close_price = float(row['Close'].iloc[0])

        is_open_equal_low = open_price == low_price
        is_high_equal_close = high_price == close_price
        is_open_equal_high = open_price == high_price
        is_low_equal_close = low_price == close_price

        prev_5 = data.iloc[-6:-1]
        all_bearish = all(prev_5['Close'] < prev_5['Open'])

        prediction = predict_bullish(model, row)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n🕒 {name} ({symbol}) - {current_time}")
        print(f"📊 OHLC - Open: {open_price:.2f}, High: {high_price:.2f}, Low: {low_price:.2f}, Close: {close_price:.2f}")
        print(f"🔍 Conditions: O=L? {is_open_equal_low}, H=C? {is_high_equal_close}, O=H? {is_open_equal_high}, L=C? {is_low_equal_close}")
        print(f"🔍 Previous 5 candles bearish? {all_bearish}")
        print(f"🤖 ML Prediction (Next Bullish?): {bool(prediction)}")
        print("----------------------------------------")

        # Bullish after 5 bearish
        if is_open_equal_low and is_high_equal_close and all_bearish and prediction == 1:
            print("🚨 ALERT: 5 Bearish + Bullish Prediction")
            alert_sound.play()
            notification.notify(title="📈 Stock Alert", message=f"{name}: Bullish after 5 bearish candles!", timeout=5)
            send_email(f"Bullish After Bearish - {name}",
                       f"{name} triggered bullish alert after 5 bearish candles.\nTime: {current_time}\nOHLC: {open_price}, {high_price}, {low_price}, {close_price}")
            sheet.append([name, current_time, open_price, high_price, low_price, close_price, "Bullish after bearish", "Bullish"])
            wb.save(excel_file)
            plot_candlestick(data, name)

        # Simple Bullish
        elif is_open_equal_low and is_high_equal_close and prediction == 1:
            print("🚨 ALERT: Bullish condition met!")
            alert_sound.play()
            notification.notify(title="📈 Bullish Alert", message=f"{name}: Bullish move expected", timeout=5)
            send_email(f"Bullish Alert - {name}",
                       f"{name} triggered bullish alert.\nTime: {current_time}\nOHLC: {open_price}, {high_price}, {low_price}, {close_price}")
            sheet.append([name, current_time, open_price, high_price, low_price, close_price, "Bullish", "Bullish"])
            wb.save(excel_file)
            plot_candlestick(data, name)

        # Simple Bearish
        elif is_open_equal_high and is_low_equal_close and prediction == 0:
            print("🚨 ALERT: Bearish condition met!")
            alert_sound.play()
            notification.notify(title="📉 Bearish Alert", message=f"{name}: Bearish move expected", timeout=5)
            send_email(f"Bearish Alert - {name}",
                       f"{name} triggered bearish alert.\nTime: {current_time}\nOHLC: {open_price}, {high_price}, {low_price}, {close_price}")
            sheet.append([name, current_time, open_price, high_price, low_price, close_price, "Bearish", "Bearish"])
            wb.save(excel_file)
            plot_candlestick(data, name)

# Scheduler
print("🔁 Starting stock monitoring every 5 minutes... Press Ctrl+C to stop.")
schedule.every(5).minutes.do(check_conditions)

while True:
    schedule.run_pending()
    time.sleep(1)
