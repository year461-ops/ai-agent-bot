# tools.py
import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
import yfinance as yf

dl = DataLoader()

def get_stock_report(ticker):
    try:
        # ===== 台股 =====
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)

            if df.empty:
                return None

            df = df.rename(columns={'close': 'Close'}).sort_values('date')

        # ===== 美股（改用 yfinance）=====
        else:
            df = yf.download(ticker, period="2y", interval="1d", progress=False)

            if df.empty:
                return None

            df = df.reset_index()

        # ===== 防呆（避免欄位問題）=====
        if "Close" not in df.columns:
            return None

        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if len(df) < 30:
            return None

        close_price = df["Close"]

        # ===== 技術指標 =====
        ma24 = close_price.rolling(24).mean()
        bias = (close_price - ma24) / ma24 * 100

        curr = float(bias.iloc[-1])
        low = float(bias.quantile(0.05))
        high = float(bias.quantile(0.95))

        # ===== 狀態判斷 =====
        status = "⚪ 常態"
        if curr <= low:
            status = "🔥 超跌"
        elif curr >= high:
            status = "⚠️ 超買"

        return {
            "id": ticker,
            "price": float(close_price.iloc[-1]),
            "bias": curr,
            "low": low,
            "high": high,
            "status": status
        }

    except Exception as e:
        print(f"tools error: {e}")
        return None