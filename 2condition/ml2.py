import yfinance as yf
import schedule
import time
# from datetime import datetime
from datetime import datetime, time as dt_time
import pygame
import pandas as pd
import mplfinance as mpf
from plyer import notification
import openpyxl
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import smtplib
from email.mime.text import MIMEText
import os
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
load_dotenv()

# Initialize pygame mixer for sound alerts
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("pop-1.mp3")
EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

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
    # "Tata Consultancy Services": "TCS.NS",
    # "HDFC Bank": "HDFCBANK.NS",
    # "ICICI Bank": "ICICIBANK.NS",
    # "Infosys": "INFY.NS",
    # "Hindustan Unilever": "HINDUNILVR.NS",
    # "ITC": "ITC.NS",
    # "State Bank of India": "SBIN.NS",
    # "Bharti Airtel": "BHARTIARTL.NS",
    # "Larsen & Toubro": "LT.NS",
    # "Kotak Mahindra Bank": "KOTAKBANK.NS",
    # "Axis Bank": "AXISBANK.NS",
    # "Bajaj Finance": "BAJFINANCE.NS",
    # "Asian Paints": "ASIANPAINT.NS",
    # "HCL Technologies": "HCLTECH.NS",
    # "Maruti Suzuki": "MARUTI.NS",
    # "Sun Pharmaceutical": "SUNPHARMA.NS",
    # "Titan Company": "TITAN.NS",
    # "Adani Enterprises": "ADANIENT.NS",
    # "Mahindra & Mahindra": "M&M.NS",
    # "Wipro": "WIPRO.NS",
    # "Power Grid Corporation": "POWERGRID.NS",
    # "UltraTech Cement": "ULTRACEMCO.NS",
    # "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS"
}

# Email config
EMAIL_ADDRESS = "shaguftafatima444@gmail.com"
EMAIL_PASSWORD = "nkaz nrou yugv tavu"
EMAIL_RECEIVER = "shaguftafatma861@gmail.com"




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

def plot_candlestick(data, company_name):
    df = data[['Open', 'High', 'Low', 'Close']].copy()
    df.dropna(inplace=True)

    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)

    df = df.sort_index()

    if df.empty:
        print("📉 DataFrame is empty, skipping plot.")
        return

    mpf.plot(df, type='candle', style='charles', title=f'{company_name} Candlestick', ylabel='Price')

def analyze_and_alert(company_name, symbol, data):
    try:
        if data.empty or len(data) < 10:
            print(f"❌ Not enough data for {company_name}")
            return

        row = data.iloc[-1]
        open_price = float(row['Open'].iloc[-1])
        high_price = float(row['High'].iloc[-1])
        low_price = float(row['Low'].iloc[-1])
        close_price = float(row['Close'].iloc[-1])

        is_open_equal_low = open_price == low_price
        is_high_equal_close = high_price == close_price
        is_open_equal_high = open_price == high_price
        is_low_equal_close = low_price == close_price
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # print(f"\n🕒 {company_name} ({symbol}) - {current_time}")
        # print(f"📊 OHLC - Open: {open_price:.2f}, High: {high_price:.2f}, Low: {low_price:.2f}, Close: {close_price:.2f}")
        # print(f"🔍 Conditions: O=L? {is_open_equal_low}, H=C? {is_high_equal_close}")
        # print("----------------------------------------")

        # Get last 5 candles
        prev_5 = data.iloc[-6:-1]
        all_bearish = all(prev_5['Close'] < prev_5['Open'])

        # ML Prediction
        model = train_model(data.copy())
        prediction = predict_bullish(model, row)

        # --- Condition 1: Strict Bullish (O=L & H=C & 5 bearish & ML=1)
        if is_open_equal_low and is_high_equal_close and all_bearish and prediction == 1:
            alert("📈 O=L & H=C + 5 Bearish + ML Bullish", company_name, current_time, open_price, high_price, low_price, close_price, "Strict Bullish")

        # --- Condition 2: Soft Bullish (O=L & H=C & ML=1)
        elif is_open_equal_low and is_high_equal_close and prediction == 1:
            alert("📈 Bullish Setup - ML Prediction", company_name, current_time, open_price, high_price, low_price, close_price, "ML Bullish")

        # --- Condition 3: Bearish (O=H & L=C & ML=0)
        # elif is_open_equal_high and is_low_equal_close and prediction == 0:
        #     alert("📉 Bearish Setup", company_name, current_time, open_price, high_price, low_price, close_price, "Bearish")

        # --- Condition 4: Basic O=L & H=C without ML
        # elif is_open_equal_low and is_high_equal_close:
        #     alert("📈 O=L and H=C Match", company_name, current_time, open_price, high_price, low_price, close_price, "Simple Bullish")

    except Exception as e:
        print(f"⚠️ Error analyzing {company_name}: {e}")


def alert(title, company, time, o, h, l, c, signal):
    print(f"🚨 ALERT: {title}")
    alert_sound.play()
    notification.notify(title=title, message=f"{company}: {signal}", timeout=5)
    send_email(f"{title} - {company}",
               f"{company} Alert:\nTime: {time}\nOHLC: {o}, {h}, {l}, {c}\nSignal: {signal}")
    sheet.append([company, time, o, h, l, c, signal, signal])
    wb.save(excel_file)
    plot_candlestick(yf.download(companies[company], period="2d", interval="5m", auto_adjust=True, progress=False), company)


def check_conditions():
    for company_name, symbol in companies.items():
        data = yf.download(symbol, period="2d", interval="5m", auto_adjust=True, progress=False)
        analyze_and_alert(company_name, symbol, data)



def is_market_open():
    current_time = datetime.now().time()
    market_open_time = dt_time(9, 15)   # 9:15 AM
    market_close_time = dt_time(15, 30) # 3:30 PM

    # Agar current time market open aur close ke beech hai to True return karega
    return market_open_time <= current_time <= market_close_time

def scheduled_job():
    if is_market_open():
        check_conditions()
    else:
        print("Market closed, monitoring paused.")

# Schedule function updated to use scheduled_job instead of check_conditions directly
# plot_candlestick()

schedule.every(1).minutes.do(scheduled_job)
# Schedule to run every 5 minutes
# schedule.every(1).minutes.do(check_conditions)
def scheduled_job():
    if is_market_open():
        check_conditions()
    else:
        print("Market closed, skipping checks...")

# Schedule the job to run every 5 minutes
schedule.every(5).minutes.do(scheduled_job)

print("🔁 Stock monitoring started...")

while True:
    schedule.run_pending()
    time.sleep(1)



