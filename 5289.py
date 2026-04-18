import pandas as pd
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask
from rich.console import Console
from rich.table import Table
from rich.live import Live

# 確保基礎套件
try:
    import yfinance as yf
    from FinMind.data import DataLoader
    from yahooquery import Ticker as YQTicker
except ImportError:
    print("❌ 缺少套件，請執行: pip install yfinance FinMind yahooquery rich flask requests")
    exit()

# ========================
# 🔧 配置區 (已校準戰情群組 ID)
# ========================
TELEGRAM_TOKEN = "8604408924:AAFDIhFyiMpSZ5KnzqW7JgTDf4SY9i6PJxA"
CHAT_IDS = ["785298601", "-1003968728718"] 

TICKER_GROUPS = {
    "🌍 全球大盤指標": ["^TWII", "^SOX", "QQQ"],
    "💎 半導體三巨頭": ["2330", "NVDA", "ASML"],
    "🚀 AI 供應鏈核心": ["2382", "6669", "3231"],
    "📈 戰略成長標的": ["5289", "MU", "ONDS"]
}

TICKER_NAMES = {
    "^TWII": "臺股加權", "^SOX": "費半指數", "QQQ": "納斯達克",
    "2330": "臺積電", "NVDA": "輝達", "ASML": "艾司摩爾",
    "2382": "廣達", "6669": "緯穎", "3231": "緯創",
    "5289": "宜鼎", "MU": "美光", "ONDS": "Ondas"
}

SCAN_INTERVAL = 600
console = Console()
app = Flask(__name__)
dl = DataLoader()

def send_telegram(message):
    for cid in CHAT_IDS:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": cid, "text": message, "parse_mode": "Markdown"}
        try: requests.post(url, data=payload, timeout=12)
        except: pass

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
        curr_bias = float(bias.iloc[-1])
        # 取得過去兩年的 5% 與 95% 分位數作為界限
        low, high = float(bias.quantile(0.05)), float(bias.quantile(0.95))
        return {"bias": curr_bias, "bounds": (low, high)}
    except: return None

def monitor_and_sync():
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    table = Table(title=f"🛡️ 全球科技戰略監控 ({now_str})", header_style="bold magenta", border_style="bright_blue")
    table.add_column("名稱", style="cyan")
    table.add_column("目前乖離", justify="right")
    table.add_column("定義區間 (低~高)", justify="center")
    table.add_column("狀態", justify="center")

    tele_report = f"🛡️ *全球科技戰略監控報表*\n時間: `{now_str}`\n"
    tele_report += "\n📊 *乖離率區間定義 (過去 2 年統計)：*\n"

    for group_name, tickers in TICKER_GROUPS.items():
        tele_report += f"\n📌 *{group_name}*\n"
        for ticker in tickers:
            res = analyze_stock(ticker)
            name = TICKER_NAMES.get(ticker, ticker)
            if not res: continue
            
            bias, low, high = res['bias'], res['bounds'][0], res['bounds'][1]
            
            if bias <= low:
                icon, status, color = "🔥", "*超跌買點*", "[bold green]"
            elif bias >= high:
                icon, status, color = "⚠️", "*超買警戒*", "[bold red]"
            else:
                icon, status, color = "⚪", "常態分佈", "[white]"
            
            # 更新 VS Code 表格
            table.add_row(name, f"{bias:.2f}%", f"{low:.1f}% ~ {high:.1f}%", f"{color}{status}[/]")
            
            # 更新 Telegram 報表 (重點：顯示區間)
            tele_report += f"{icon} `{name}`: `{bias:.2f}%` ({status})\n"
            tele_report += f"    └ 正常區間: `{low:.1f}%` ~ `{high:.1f}%`\n"

    send_telegram(tele_report)
    return table

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080, use_reloader=False), daemon=True).start()
    console.print("[bold green]🌟 戰略雷達 7.0 啟動：動態區間定義已加入報表！[/]")
    with Live(monitor_and_sync(), refresh_per_second=0.1) as live:
        while True:
            live.update(monitor_and_sync())
            time.sleep(SCAN_INTERVAL)