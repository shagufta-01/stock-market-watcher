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

# Initialize pygame mixer for sound alerts
pygame.mixer.init()
alert_sound = pygame.mixer.Sound("alert.mp3")

# Excel logging
excel_file = "matched_conditions.xlsx"
try:
    wb = openpyxl.load_workbook(excel_file)
    sheet = wb.active
except FileNotFoundError:
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.append(["Company", "Date", "Open", "High", "Low", "Close", "ML_Prediction"])

# Stock watchlist
companies = {
    "Bajaj Finance": "BAJFINANCE.NS",
}

# ML Prediction Function
def train_model(df):
    df = df.copy()
    df['Target'] = (df['Close'].shift(-1) > df['Open'].shift(-1)).astype(int)
    df.dropna(inplace=True)

    X = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    y = df['Target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    return model

def predict_bullish(model, row):
    X_pred = row[['Open', 'High', 'Low', 'Close', 'Volume']].values.reshape(1, -1)
    return model.predict(X_pred)[0]

# Candlestick plot
def plot_candlestick(df, name):
    df = df.tail(20).copy()
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].dropna().astype(float)
    mpf.plot(df, type='candle', style='charles', title=name, ylabel='Price')

# Main check function
def check_conditions():
    for name, symbol in companies.items():
        data = yf.download(symbol, period="2d", interval="5m", auto_adjust=True)

        if data.empty or len(data) < 10:
            print(f"❌ Not enough data for {name}")
            continue

        model = train_model(data.copy())

        latest = data.tail(1)
        row = latest.iloc[0]
        open_price = float(row['Open'])
        high_price = float(row['High'])
        low_price = float(row['Low'])
        close_price = float(row['Close'])

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🕒 {name} ({symbol}) - {current_time}")
        print(f"📊 OHLC - Open: {open_price:.2f}, High: {high_price:.2f}, Low: {low_price:.2f}, Close: {close_price:.2f}")

        is_open_equal_low = open_price == low_price
        is_high_equal_close = high_price == close_price

        print(f"🔍 Conditions: Open=Low? {is_open_equal_low}, High=Close? {is_high_equal_close}")

        prediction = predict_bullish(model, row)
        print(f"🤖 ML Prediction (Next Candle Bullish?): {bool(prediction)}")
        print("----------------------------------------")

        if is_open_equal_low and is_high_equal_close and prediction == 1:
            print("🚨 ALERT: Condition matched + ML predicts bullish move!")

            alert_sound.play()

            notification.notify(
                title="📈 ML Stock Alert!",
                message=f"{name}: Match + ML predicts bullish candle",
                timeout=5
            )

            sheet.append([name, current_time, open_price, high_price, low_price, close_price, "Bullish"])
            wb.save(excel_file)

            plot_candlestick(data, name)

# Run every 5 minutes
print("Starting scheduler... Press Ctrl+C to stop")
schedule.every(5).minutes.do(check_conditions)

while True:
    schedule.run_pending()
    time.sleep(1)
