# tools.py
import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
from yahooquery import Ticker as YQTicker

dl = DataLoader()

def get_stock_report(ticker):
    try:
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)
            if df.empty: return None
            df = df.rename(columns={'close': 'Close'}).sort_values('date')
        else:
            q = YQTicker(ticker)
            df = q.history(period='2y', interval='1d').reset_index()

        df['Close'] = pd.to_numeric(df['Close'])
        close_price = df['Close']

        ma24 = close_price.rolling(24).mean()
        bias = (close_price - ma24) / ma24 * 100

        curr = float(bias.iloc[-1])
        low, high = float(bias.quantile(0.05)), float(bias.quantile(0.95))

        status = "⚪ 常態"
        if curr <= low: status = "🔥 超跌"
        elif curr >= high: status = "⚠️ 超買"

        return {
            "ticker": ticker,
            "price": float(close_price.iloc[-1]),
            "bias": curr,
            "low": low,
            "high": high,
            "status": status
        }

    except:
        return None