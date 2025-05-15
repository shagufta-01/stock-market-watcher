
# 📈 Live Stock Market Watcher with Candlestick Chart

A Python-based stock market monitoring tool that checks live market data for a specific condition and plays a sound + shows notification when it matches. Also displays a live candlestick chart and logs data to Excel.

---

## 🔧 Features

- 🔍 Monitors stock every 5 minutes
- ✅ Triggers alert when: `Open = Low` and `High = Close`
- 🎵 Plays sound alert (`.mp3`) when condition is met
- 📢 Shows desktop notification using Plyer
- 🕵️ Logs data to an Excel file `StockMarket_log.xlsx`
- 🕯️ Displays live candlestick chart using `mplfinance`

---

## 🛠️ Tech Stack

- Python
- yFinance
- mplfinance
- openpyxl
- plyer
- matplotlib
- pygame
- schedule

---

## 🚀 How to Run

1. **Clone the project**
   bash
   git clone <your-repo-url>
   cd stockM


2. **Install dependencies**

   ```bash
   pip install yfinance schedule pygame openpyxl plyer mplfinance matplotlib
   ```

3. **Run the main file**

   ```bash
   python main1.py
   ```

---

## 📊 Sample Condition

If:

* `open == low`
* `high == close`

Then:

* Sound alert will be played
* Desktop notification is shown
* Excel log is updated
* Candle chart is refreshed

---

## 📁 Log File

`StockMarket_log.xlsx` will contain:

| Timestamp           | Company  | Ticker      | Open | Low | High | Close | Matched |
| ------------------- | -------- | ----------- | ---- | --- | ---- | ----- | ------- |
| 2025-05-15 12:55:00 | Reliance | RELIANCE.NS | ...  | ... | ...  | ...   | Yes/No  |

---

## 💡 Future Scope

* Add support for multiple stocks
* Add Telegram or email alerts
* Export candle chart image

---

## 👤 Shagufta Fatima

* **Your Name Here**
* 📧 [shaguftafatima444@gmail.com](mailto:shaguftafatima444@gmail.com)



