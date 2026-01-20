import ccxt, pandas as pd, ta, time
from telegram import Bot

# ================= CONFIG =================
TOKEN = "8396825421:AAEh05k1lWAlsEoToKQBq9hn9VDoCetoQao"
CHAT_ID = 5505106909
TIMEFRAME = "15m"

TP_PERCENT = 1.5
SL_PERCENT = 1.0

RSI_BUY_MAX = 65
RSI_SELL_MIN = 35
EMA_DISTANCE_MIN = 0.15

SR_LOOKBACK = 50
SR_ZONE = 0.5  # persen

PAIRS = [
    "BTC/USDT","ETH/USDT","BNB/USDT","SOL/USDT","XRP/USDT",
    "ADA/USDT","AVAX/USDT","DOGE/USDT","LINK/USDT","MATIC/USDT"
]
# =========================================

exchange = ccxt.binance()
bot = Bot(token=TOKEN)
last_signal = {}

def near_level(price, level):
    return abs((price - level) / level) * 100 <= SR_ZONE

def check_signal(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=100)
    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])

    df['ema9'] = ta.trend.ema_indicator(df['c'], 9)
    df['ema21'] = ta.trend.ema_indicator(df['c'], 21)
    df['rsi'] = ta.momentum.rsi(df['c'], 14)

    last = df.iloc[-1]
    price = last['c']

    # ===== SUPPORT & RESISTANCE =====
    support = df['l'].tail(SR_LOOKBACK).min()
    resistance = df['h'].tail(SR_LOOKBACK).max()

    ema_gap = abs((last['ema9'] - last['ema21']) / price) * 100

    # ===== BUY =====
    if (
        last['ema9'] > last['ema21'] and
        last['rsi'] < RSI_BUY_MAX and
        ema_gap > EMA_DISTANCE_MIN and
        near_level(price, support)
    ):
        tp = round(price * (1 + TP_PERCENT / 100), 4)
        sl = round(price * (1 - SL_PERCENT / 100), 4)
        return "BUY", price, tp, sl, last['rsi'], support, resistance

    # ===== SELL =====
    if (
        last['ema9'] < last['ema21'] and
        last['rsi'] > RSI_SELL_MIN and
        ema_gap > EMA_DISTANCE_MIN and
        near_level(price, resistance)
    ):
        tp = round(price * (1 - TP_PERCENT / 100), 4)
        sl = round(price * (1 + SL_PERCENT / 100), 4)
        return "SELL", price, tp, sl, last['rsi'], support, resistance

    return None, None, None, None, None, None, None

while True:
    for pair in PAIRS:
        signal, price, tp, sl, rsi, sup, res = check_signal(pair)

        if signal and last_signal.get(pair) != signal:
            msg = f"""
📊 SIGNAL KRIPTO ({signal})

Pair : {pair}
TF   : 15 Menit

Entry : {round(price,4)}
TP    : {tp}
SL    : {sl}

Support    : {round(sup,4)}
Resistance : {round(res,4)}
RSI        : {round(rsi,2)}

📌 Entry di area S/R valid
"""
            bot.send_message(chat_id=CHAT_ID, text=msg)
            last_signal[pair] = signal

    time.sleep(300)
