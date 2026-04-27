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
            df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

        # ========================
        # 美股（穩定版）
        # ========================
        else:
            # ---------- 1️⃣ yfinance ----------
            try:
                yf_df = yf.download(ticker, period="2y", interval="1d", progress=False)

                if yf_df is not None and not yf_df.empty:
                    yf_df = yf_df.reset_index()

                    # 統一 Close 欄位
                    if "Adj Close" in yf_df.columns:
                        yf_df = yf_df.rename(columns={"Adj Close": "Close"})
                    elif "Close" not in yf_df.columns:
                        yf_df = None

                    if yf_df is not None:
                        df = yf_df

            except Exception as e:
                print(f"yfinance error for {ticker}: {e}")

            # ---------- 2️⃣ yahooquery fallback ----------
            if df is None:
                try:
                    q = YQTicker(ticker)
                    yq = q.history(period="2y", interval="1d")

                    if yq is not None and isinstance(yq, pd.DataFrame) and not yq.empty:

                        # MultiIndex 處理
                        if isinstance(yq.index, pd.MultiIndex):
                            yq = yq.reset_index()

                        yq.columns = [c.lower() for c in yq.columns]

                        if "adjclose" in yq.columns:
                            yq = yq.rename(columns={"adjclose": "Close"})
                        elif "close" in yq.columns:
                            yq = yq.rename(columns={"close": "Close"})
                        else:
                            yq = None

                        if yq is not None:
                            df = yq

                except Exception as e:
                    print(f"yahooquery error for {ticker}: {e}")

            if df is None:
                return None

        # ========================
        # 資料清理
        # ========================
        if "Close" not in df.columns:
            return None

        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if len(df) < 30:
            return None

        close_price = df["Close"]

        # ========================
        # 計算乖離率
        # ========================
        ma24 = close_price.rolling(24).mean()
        bias = (close_price - ma24) / ma24 * 100

        curr = float(bias.iloc[-1])
        low = float(bias.quantile(0.05))
        high = float(bias.quantile(0.95))

        # 狀態判斷
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