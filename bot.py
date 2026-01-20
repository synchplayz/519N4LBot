import ccxt, pandas as pd, ta, time
from telegram import Bot

# ================= CONFIG =================
TOKEN = "8396825421:AAEh05k1lWAlsEoToKQBq9hn9VDoCetoQao"
CHAT_ID = "5505106909"
TIMEFRAME = "15m"

PAIRS = [
    "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT",
    "ADA/USDT","AVAX/USDT","DOGE/USDT","LINK/USDT","MATIC/USDT"
]

# =========================================

exchange = ccxt.binance()
bot = Bot(token=TOKEN)
last_signal = {}

def check_signal(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=100)
    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])

    df['ema9'] = ta.trend.ema_indicator(df['c'], 9)
    df['ema21'] = ta.trend.ema_indicator(df['c'], 21)
    df['rsi'] = ta.momentum.rsi(df['c'], 14)

    last = df.iloc[-1]

    if last['ema9'] > last['ema21'] and last['rsi'] < 70:
        return "BUY", round(last['c'],2), round(last['rsi'],2)

    if last['ema9'] < last['ema21'] and last['rsi'] > 30:
        return "SELL", round(last['c'],2), round(last['rsi'],2)

    return None, None, None

while True:
    for pair in PAIRS:
        signal, price, rsi = check_signal(pair)

        if signal and last_signal.get(pair) != signal:
            msg = f"""
📊 SIGNAL KRIPTO

Pair : {pair}
TF   : 15 Menit
Signal : {signal}

Harga : {price}
RSI   : {rsi}

⚠️ Bukan saran keuangan
"""
            bot.send_message(chat_id=CHAT_ID, text=msg)
            last_signal[pair] = signal

    time.sleep(300)  # cek tiap 5 menit
