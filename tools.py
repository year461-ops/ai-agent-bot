import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
from yahooquery import Ticker as YQTicker

dl = DataLoader()

def get_stock_report(ticker):
    try:
        # ===== 台股邏輯 =====
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)
            if df.empty: return None
            df = df.rename(columns={'close': 'Close'}).sort_values('date')

        # ===== 美股邏輯 (YahooQuery 版) =====
        else:
            q = YQTicker(ticker)
            df = q.history(period='2y', interval='1d')
            if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                return None
            
            df = df.reset_index()
            # 統一欄位名稱
            df = df.rename(columns={'adjclose': 'Close', 'close': 'Close', 'date': 'Date'})

        if "Close" not in df.columns: return None

        # 確保數字格式
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])
        if len(df) < 30: return None

        close_price = df["Close"]

        # ===== 計算 24 日乖離率 (BIAS) =====
        ma24 = close_price.rolling(24).mean()
        bias = (close_price - ma24) / ma24 * 100

        curr = float(bias.iloc[-1])
        low = float(bias.quantile(0.05))
        high = float(bias.quantile(0.95))

        # 狀態判斷
        status = "⚪ 常態"
        if curr <= low: status = "🔥 超跌"
        elif curr >= high: status = "⚠️ 超買"

        return {
            "id": ticker.upper(),
            "price": round(float(close_price.iloc[-1]), 2),
            "bias": round(curr, 2),
            "low": round(low, 2),
            "high": round(high, 2),
            "status": status
        }

    except Exception as e:
        print(f"Error for {ticker}: {e}")
        return None