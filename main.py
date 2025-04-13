import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

WEBHOOK = "https://discord.com/api/webhooks/1361080639775965204/CL2KP0wGbKzPVGYWFpHdGs00ZCPo-TFi5YyDwgXTls8dITEvJk5gGEierrqxW9plsxbP"
SUPER_NARROW_THRESHOLD = 0.1
NARROW_THRESHOLD = 0.25

# Sample NSE stock list (expand as needed)
nse_symbols = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "SBIN.NS", "LT.NS", "AXISBANK.NS", "KOTAKBANK.NS", "HINDUNILVR.NS"
]

def calculate_cpr(high, low, close):
    pp = (high + low + close) / 3
    bc = (high + low) / 2
    tc = 2 * pp - bc
    width = abs(tc - bc)
    return pp, bc, tc, width

def fetch_and_scan(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1d",auto_adjust=False, progress=False)
        if len(data) < 2:
            return None

        prev_day = data.iloc[-2]
        high, low, close = prev_day['High'], prev_day['Low'], prev_day['Close']
        _, bc, tc, width = calculate_cpr(high, low, close)
        width_pct = round((width / close) * 100, 4)
        return symbol, float(width_pct)
    except:
        return None

def main():
    narrow = []
    super_narrow = []
    all_lines = []

    for symbol in nse_symbols:
        result = fetch_and_scan(symbol)
        if result:
            sym, pct = result
            line = f"{sym}: {pct}%"
            all_lines.append(line)
            if pct <= SUPER_NARROW_THRESHOLD:
                super_narrow.append(line)
            elif pct <= NARROW_THRESHOLD:
                narrow.append(line)

    # Compose message
    msg = "**🇮🇳 Indian Stock CPR Scan**\n\n"
    msg += f"🟣 **Super Narrow** ({len(super_narrow)}):\n" + "\n".join(super_narrow) + "\n\n"
    msg += f"🔵 **Narrow** ({len(narrow)}):\n" + "\n".join(narrow)
    requests.post(WEBHOOK, json={"content": msg})

    # Export .txt and send to Discord
    with open("cpr_results.txt", "w") as f:
        f.write("\n".join(all_lines))

    with open("cpr_results.txt", "rb") as f:
        requests.post(WEBHOOK, files={"file": f})

if __name__ == "__main__":
    main()
