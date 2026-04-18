import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
from yahooquery import Ticker as YQTicker  # 🔥 改用 yahooquery

dl = DataLoader()

def get_stock_report(ticker):
    try:
        # ===== 台股邏輯 (維持不變) =====
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)

            if df.empty:
                print("台股抓不到:", ticker)
                return None

            df = df.rename(columns={'close': 'Close'}).sort_values('date')

        # ===== 美股邏輯 (切換為 yahooquery 穩定版) =====
        else:
            try:
                # 1. 初始化 Ticker (會自動處理大小寫)
                q = YQTicker(ticker)
                
                # 2. 抓取歷史數據 (yahooquery 預設會處理除權息)
                df = q.history(period='2y', interval='1d')

                if df is None or (isinstance(df, pd.DataFrame) and df.empty):
                    print(f"美股抓不到 (Empty): {ticker}")
                    return None
                
                # 3. 重要：yahooquery 返回的是 MultiIndex (symbol, date)
                # 我們需要重設 index 把它轉成標準格式
                df = df.reset_index()

                # 4. 統一欄位名稱
                # yahooquery 的欄位通常是小寫 'adjclose' 或 'close'
                if 'adjclose' in df.columns:
                    df = df.rename(columns={'adjclose': 'Close'})
                elif 'close' in df.columns:
                    df = df.rename(columns={'close': 'Close'})
                
                if 'date' in df.columns:
                    df = df.rename(columns={'date': 'Date'})

            except Exception as e:
                print(f"YahooQuery 抓取錯誤 ({ticker}):", e)
                return None

        # ===== 共通數據處理與防呆 =====
        if df is None or "Close" not in df.columns:
            return None

        # 確保 Close 是數字型態且移除空值
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if len(df) < 30:
            print(f"數據長度不足 ({ticker}): {len(df)}")
            return None

        close_price = df["Close"]

        # ===== 指標計算 (BIAS 24) =====
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
            "id": ticker.upper(),
            "price": float(close_price.iloc[-1]),
            "bias": curr,
            "low": low,
            "high": high,
            "status": status
        }

    except Exception as e:
        print(f"tools 總體錯誤 ({ticker}):", e)
        return None