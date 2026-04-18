import yfinance as yf
import pandas as pd
import time
import requests
import threading
from datetime import datetime
from flask import Flask
from rich.console import Console
from rich.table import Table
from rich.live import Live

# ========================
# 🔧 關鍵金鑰與配置區
# ========================
TELEGRAM_TOKEN = "8735155402:AAEeu1e2HMezFnRMDDZQ5X2AIWclOe-2Ojo"
CHAT_ID = "785298601"

# 你的監控池
MY_HOLDINGS = ["5289.TW"]  # 宜鼎：核心持股
AI_SEMICON_POOL = [
    "NVDA", "TSM", "AVGO", "MU", "ONDS",        # 美股 AI/半導體
    "2330.TW", "2454.TW", "2382.TW", "6669.TW", # 台股 AI/半導體
    "3231.TW", "2376.TW", "3661.TW"
]

SCAN_INTERVAL = 600  # 每 10 分鐘掃描一次 (可自行縮短)
last_alerts = {}     # 紀錄狀態，避免重複發送

console = Console()
app = Flask(__name__)

# ========================
# 📡 雲端防休眠模組 (Flask)
# ========================
@app.route('/')
def home():
    return f"股票監控雷達運行中... 最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def run_flask():
    # 這裡的 port 8080 是雲端服務常用的端口
    app.run(host='0.0.0.0', port=8080)

# ========================
# 🧠 智慧分析模組
# ========================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        console.print(f"[red]Telegram 發送失敗: {e}[/red]")

def analyze_stock(ticker):
    # 抓取 2 年資料以獲取準確的歷史乖離分位數
    df = yf.download(ticker, period='2y', interval='1d', progress=False)
    if df.empty or len(df) < 24: return None
    
    # 計算 24 日均線與乖離率
    df['MA24'] = df['Close'].rolling(window=24).mean()
    df['BIAS'] = (df['Close'] - df['MA24']) / df['MA24'] * 100
    
    # 自動識別「股性」：歷史極端 5% 與 95% 區域
    lower_bound = df['BIAS'].quantile(0.05)
    upper_bound = df['BIAS'].quantile(0.95)
    
    curr_price = df['Close'].iloc[-1].item()
    curr_bias = df['BIAS'].iloc[-1]
    
    # 成交量因子：今日量是否大於 5 日均量 1.5 倍
    df['Vol_MA5'] = df['Volume'].rolling(5).mean()
    is_vol_spike = df['Volume'].iloc[-1] > (df['Vol_MA5'].iloc[-1] * 1.5)
    
    return {
        "price": curr_price,
        "bias": curr_bias,
        "bounds": (lower_bound, upper_bound),
        "vol_spike": is_vol_spike
    }

def monitor_cycle():
    all_tickers = MY_HOLDINGS + AI_SEMICON_POOL
    table = Table(title=f"📡 AI/半導體監控雷達 ({datetime.now().strftime('%H:%M:%S')})")
    table.add_column("代碼", style="cyan")
    table.add_column("現價", justify="right")
    table.add_column("乖離率", justify="right")
    table.add_column("歷史低點/高點", justify="center")
    table.add_column("狀態", justify="center")

    for ticker in all_tickers:
        res = analyze_stock(ticker)
        if not res: continue
        
        price = res['price']
        bias = res['bias']
        low, high = res['bounds']
        is_holding = ticker in MY_HOLDINGS
        
        status_text = "[white]盤整[/white]"
        alert_status = "Normal"

        # 邏輯判定
        if bias <= low:
            status_text = "[bold green]🔥 超跌 (買點)[/bold green]"
            alert_status = "Oversold"
        elif bias >= high:
            status_text = "[bold red]⚠️ 超買 (過熱)[/bold red]"
            alert_status = "Overbought"
        
        # 發送 Telegram 警報
        if last_alerts.get(ticker) != alert_status:
            if alert_status != "Normal":
                icon = "🚨【核心持股】" if is_holding else "📊【產業機會】"
                spike_note = "\n⚠️ *注意：今日成交量明顯放大！*" if res['vol_spike'] else ""
                msg = f"{icon} *{ticker}*\n價格：`{price:.2f}`\n乖離率：`{bias:.2f}%` (歷史極值：{low:.1f}% ~ {high:.1f}%){spike_note}\n狀態：{'進入超跌反彈區' if alert_status == 'Oversold' else '進入高檔過熱區'}"
                send_telegram(msg)
            last_alerts[ticker] = alert_status

        table.add_row(ticker, f"{price:.2f}", f"{bias:.2f}%", f"{low:.1f}% / {high:.1f}%", status_text)
    
    return table

# ========================
# 🏃 啟動流程
# ========================
if __name__ == "__main__":
    # 1. 啟動背景 Flask 網頁 (用於防休眠)
    # 若只是在本地 VS Code 跑，這行可以保留不影響功能
    threading.Thread(target=run_flask, daemon=True).start()
    
    console.print("[bold yellow]🚀 監控雷達啟動中...[/bold yellow]")
    console.print(f"核心監控持股: [bold cyan]{MY_HOLDINGS}[/bold cyan]")
    
    # 2. 啟動主監控迴圈
    with Live(monitor_cycle(), refresh_per_second=0.1) as live:
        while True:
            live.update(monitor_cycle())
            time.sleep(SCAN_INTERVAL)