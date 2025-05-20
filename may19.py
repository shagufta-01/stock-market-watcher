import yfinance as yf
import pandas as pd
from datetime import datetime
import schedule
import time
import pygame
from plyer import notification
import smtplib
from email.message import EmailMessage
import openpyxl
import os
import mplfinance as mpf

# Initialize sound
pygame.mixer.init()
alert_sound_path = "alert.wav"  # Make sure this file exists in the same directory

# Stock list
watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

# Log to Excel
def log_to_excel(symbol, row):
    filename = f"{symbol}_alerts.xlsx"
    if not os.path.exists(filename):
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.append(["Time", "Open", "High", "Low", "Close", "Condition", "ML Prediction"])
        wb.save(filename)
    wb = openpyxl.load_workbook(filename)
    sheet = wb.active
    sheet.append(row)
    wb.save(filename)

# Sound alert
def play_sound():
    pygame.mixer.music.load(alert_sound_path)
    pygame.mixer.music.play()

# Desktop notification
def show_notification(title, message):
    notification.notify(title=title, message=message, timeout=10)

# Email alert
def send_email(subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"  # Replace
    msg['To'] = "receiver_email@gmail.com"  # Replace

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("your_email@gmail.com", "your_app_password")  # Replace
            smtp.send_message(msg)
    except Exception as e:
        print("Email error:", e)

# Check stock conditions
def check_conditions(symbol):
    try:
        data = yf.download(tickers=symbol, interval="5m", period="1d")
        if len(data) < 6:
            return

        last = data.iloc[-1]
        o, h, l, c = last['Open'], last['High'], last['Low'], last['Close']
        condition = ""
        condition_met = False

        if round(o, 2) == round(l, 2) and round(h, 2) == round(c, 2):
            condition = "Bullish Setup (Open=Low and High=Close)"
            condition_met = True
        elif all(data['Close'].iloc[-i] < data['Open'].iloc[-i] for i in range(1, 6)):
            condition = "5 Consecutive Bearish Candles"
            condition_met = True

        prediction = 1 if c > o else 0

        if condition_met:
            message = f"{symbol}: {condition}"
            details = f"""
🔔 {message}
Time  = {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Open  = {o:.2f}
High  = {h:.2f}
Low   = {l:.2f}
Close = {c:.2f}
ML Prediction = {"Bullish" if prediction else "Bearish"}
"""
            print(details)
            play_sound()
            show_notification("Stock Alert", message)
            send_email("Stock Condition Alert", details)
            log_to_excel(symbol, [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), o, h, l, c, condition, prediction])
            mpf.plot(data.tail(30), type='candle', volume=True, title=symbol)

    except Exception as e:
        print(f"Error checking {symbol}: {e}")

# Schedule every 5 minutes
for symbol in watchlist:
    schedule.every(5).minutes.do(check_conditions, symbol=symbol)

print("📊 Monitoring started...")
while True:
    schedule.run_pending()
    time.sleep(1)
