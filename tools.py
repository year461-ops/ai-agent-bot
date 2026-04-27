import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
from yahooquery import Ticker as YQTicker
import yfinance as yf

dl = DataLoader()

def get_stock_report(ticker):
    try:
        df = None

        # ========================
        # 台股
        # ========================
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)

            if df is None or df.empty:
                return None

            df = df.rename(columns={'close': 'Close'}).sort_values('date')

        # ========================
        # 美股（修正版）
        # ========================
        else:
            try:
                df = yf.download(ticker, period="2y", interval="1d", progress=False)

                if df is None or df.empty:
                    return None

                # 🔥 關鍵修正：MultiIndex → 單欄
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                df = df.reset_index()

                # 統一 Close
                if "Adj Close" in df.columns:
                    df = df.rename(columns={"Adj Close": "Close"})

                if "Close" not in df.columns:
                    return None

            except Exception as e:
                print(f"yfinance error: {e}")
                return None

        # ========================
        # 數據清理
        # ========================
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if len(df) < 30:
            return None

        # 🔥 關鍵：確保是 Series
        close_price = df["Close"]

        # ========================
        # 計算乖離
        # ========================
        ma24 = close_price.rolling(24).mean()
        bias = (close_price - ma24) / ma24 * 100

        curr = float(bias.iloc[-1])
        low = float(bias.quantile(0.05))
        high = float(bias.quantile(0.95))

        status = "⚪ 常態"
        if curr <= low:
            status = "🔥 超跌"
        elif curr >= high:
            status = "⚠️ 超買"

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