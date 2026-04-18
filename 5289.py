import pandas as pd
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask
from rich.console import Console
from rich.table import Table
from rich.live import Live

try:
    import yfinance as yf
    from FinMind.data import DataLoader
    from yahooquery import Ticker as YQTicker
except ImportError:
    print("❌ 缺少套件，請執行: pip install yfinance FinMind yahooquery rich flask requests")
    exit()

# ========================
# 🔧 關鍵配置區 (地址已校準)
# ========================
TELEGRAM_TOKEN = "8604408924:AAFDIhFyiMpSZ5KnzqW7JgTDf4SY9i6PJxA"

# 同時發送給個人 ID 與 戰情群組 ID
CHAT_IDS = ["785298601", "-1003968728718"] 

TICKER_GROUPS = {
    "⭐ 核心持股": ["5289"],
    "🏢 宜鼎生態系 (IPC/儲存)": ["2395", "6414", "3088", "MU"],
    "🚀 AI/半導體主流": ["NVDA", "2330", "2382", "6669", "3231"],
    "🌍 大盤與產業指標": ["^TWII", "^SOX", "ONDS"] 
}

TICKER_NAMES = {
    "5289": "宜鼎 (核心)", "2395": "研華 (IPC龍頭)", "6414": "樺漢 (IPC大廠)",
    "3088": "艾訊 (IPC指標)", "MU": "美光 (記憶體風向)", "NVDA": "輝達 (AI領頭羊)",
    "2330": "臺積電 (權值王)", "2382": "廣達 (AI伺服器)", "6669": "緯穎 (雲端供應)",
    "3231": "緯創 (AI代工)", "^TWII": "臺股加權指數", "^SOX": "費城半導體指數", "ONDS": "Ondas (邊緣AI傳輸)"
}

SCAN_INTERVAL = 600
console = Console()
app = Flask(__name__)
dl = DataLoader()

def send_telegram(message):
    for cid in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": cid, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, data=payload, timeout=12)
        except:
            pass

def analyze_stock(ticker):
    df = None
    try:
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)
            if not df.empty:
                df = df.rename(columns={'close': 'Close', 'date': 'Date'})
                df['Close'] = pd.to_numeric(df['Close'])
        
        if df is None or df.empty:
            yt = ticker if "^" in ticker or "." in ticker else ticker
            q = YQTicker(yt)
            hist = q.history(period='2y', interval='1d')
            if not hist.empty:
                df = hist.reset_index()
                for col in ['adjclose', 'adj_close', 'close']:
                    if col in df.columns:
                        df = df.rename(columns={col: 'Close'})
                        break

        if df is None or df.empty or len(df) < 24: return None
        close_price = df['Close']
        ma24 = close_price.rolling(window=24).mean()
        bias = (close_price - ma24) / ma24 * 100
        curr_price, curr_bias = float(close_price.iloc[-1]), float(bias.iloc[-1])
        low, high = float(bias.quantile(0.05)), float(bias.quantile(0.95))
        return {"price": curr_price, "bias": curr_bias, "bounds": (low, high)}
    except: return None

def monitor_and_sync():
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    table = Table(title=f"🛡️ 宜鼎戰略監控雷達 ({now_str})", header_style="bold magenta", border_style="bright_blue")
    table.add_column("群組", style="dim")
    table.add_column("名稱", style="cyan")
    table.add_column("24D 乖離", justify="right")
    table.add_column("狀態", justify="center")

    tele_report = f"🛡️ *宜鼎戰略監控報表*\n時間: `{now_str}`\n"

    for group_name, tickers in TICKER_GROUPS.items():
        tele_report += f"\n📌 *{group_name}*\n"
        for ticker in tickers:
            res = analyze_stock(ticker)
            name = TICKER_NAMES.get(ticker, ticker)
            if not res:
                table.add_row(group_name, name, "-", "[bold red]讀取失敗[/]")
                tele_report += f"• `{name}`: ⚠️ 讀取中\n"
                continue
            
            bias, low, high = res['bias'], res['bounds'][0], res['bounds'][1]
            if bias <= low: icon, status_text, color = "🔥", "超跌買點", "[bold green]"
            elif bias >= high: icon, status_text, color = "⚠️", "超買警戒", "[bold red]"
            else: icon, status_text, color = "⚪", "常態分佈", "[white]"
            
            table.add_row(group_name, name, f"{bias:.2f}%", f"{color}{status_text}[/]")
            tele_report += f"{icon} `{name}`: `{bias:.2f}%` -> *{status_text}*\n"

    send_telegram(tele_report)
    return table

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080, use_reloader=False), daemon=True).start()
    console.print("[bold green]🌟 戰情群組同步模式啟動！[/]")
    with Live(monitor_and_sync(), refresh_per_second=0.1) as live:
        while True:
            live.update(monitor_and_sync())
            time.sleep(SCAN_INTERVAL)