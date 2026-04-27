import pandas as pd
from datetime import datetime, timedelta
from FinMind.data import DataLoader
import yfinance as yf

dl = DataLoader()

# ========================
# 技術面
# ========================
def get_stock_report(ticker):
    try:
        df = None

        # 台股
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)

            if df is None or df.empty:
                return None

            df = df.rename(columns={
                'close': 'Close',
                'Trading_Volume': 'Volume'
            }).sort_values('date')

        # 美股
        else:
            df = yf.download(ticker, period="2y", interval="1d", progress=False)

            if df is None or df.empty:
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df = df.reset_index()

            if "Adj Close" in df.columns:
                df = df.rename(columns={"Adj Close": "Close"})

        if "Close" not in df.columns:
            return None

        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df["Volume"] = pd.to_numeric(df.get("Volume", 0), errors="coerce")
        df = df.dropna(subset=["Close"])

        if len(df) < 60:
            return None

        close = df["Close"]
        volume = df["Volume"]

        # 指標
        ma24 = close.rolling(24).mean()
        ma50 = close.rolling(50).mean()

        bias = (close - ma24) / ma24 * 100
        curr_bias = float(bias.iloc[-1])
        low = float(bias.quantile(0.05))
        high = float(bias.quantile(0.95))

        # RSI
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        curr_rsi = float(rsi.iloc[-1])

        # 成交量
        vol_avg = volume.rolling(20).mean()
        vol_ratio = float(volume.iloc[-1] / vol_avg.iloc[-1]) if vol_avg.iloc[-1] > 0 else 1

        trend = "多頭" if close.iloc[-1] > ma50.iloc[-1] else "空頭"

        status = "常態"
        if curr_bias <= low:
            status = "超跌"
        elif curr_bias >= high:
            status = "超買"

        score = 0
        if curr_bias <= low: score += 1
        if curr_rsi < 30: score += 1
        if close.iloc[-1] > ma50.iloc[-1]: score += 1
        if vol_ratio > 1.2: score += 1

        support = float(close.rolling(20).min().iloc[-1])
        resistance = float(close.rolling(20).max().iloc[-1])

        return {
            "id": ticker.upper(),
            "price": round(float(close.iloc[-1]), 2),
            "bias": round(curr_bias, 2),
            "low": round(low, 2),
            "high": round(high, 2),
            "rsi": round(curr_rsi, 2),
            "trend": trend,
            "status": status,
            "score": score,
            "volume_ratio": round(vol_ratio, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2)
        }

    except Exception as e:
        print(e)
        return None


# ========================
# 基本面（台股 + 美股）
# ========================
def get_fundamental_score(ticker):
    try:
        # ===== 台股（FinMind）=====
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=900)).strftime('%Y-%m-%d')

            # 營收 YoY
            rev = dl.taiwan_stock_month_revenue(stock_id=ticker, start_date=start_date)
            rev = rev.sort_values("date")
            revenue_growth = None
            if len(rev) >= 13:
                revenue_growth = (rev.iloc[-1]["revenue"] - rev.iloc[-13]["revenue"]) / rev.iloc[-13]["revenue"]

            # EPS
            fs = dl.taiwan_stock_financial_statements(stock_id=ticker, start_date=start_date)
            eps_df = fs[fs["type"] == "EPS"].sort_values("date")
            eps_growth = None
            if len(eps_df) >= 8:
                last4 = eps_df.tail(4)["value"].sum()
                prev4 = eps_df.tail(8).head(4)["value"].sum()
                eps_growth = (last4 - prev4) / prev4 if prev4 else None

            # 毛利率
            gm_df = fs[fs["type"] == "GrossMargin"].sort_values("date")
            gross_margin = float(gm_df.iloc[-1]["value"]) / 100 if len(gm_df) > 0 else None

            # P/E
            pe_df = dl.taiwan_stock_per_pbr(stock_id=ticker, start_date=start_date)
            pe_df = pe_df.sort_values("date")
            pe = float(pe_df.iloc[-1]["per"]) if len(pe_df) > 0 else None

        # ===== 美股（yfinance）=====
        else:
            tk = yf.Ticker(ticker)
            info = tk.info

            pe = info.get("trailingPE")
            gross_margin = info.get("grossMargins")

            # EPS成長（用 earnings）
            qe = tk.quarterly_earnings
            eps_growth = None
            if isinstance(qe, pd.DataFrame) and len(qe) >= 8:
                last4 = qe.tail(4)["Earnings"].sum()
                prev4 = qe.tail(8).head(4)["Earnings"].sum()
                eps_growth = (last4 - prev4) / prev4 if prev4 else None

            # 營收成長
            qf = tk.quarterly_financials
            revenue_growth = None
            if isinstance(qf, pd.DataFrame) and "Total Revenue" in qf.index:
                cols = list(qf.columns)
                if len(cols) >= 8:
                    last4 = qf.loc["Total Revenue", cols[:4]].sum()
                    prev4 = qf.loc["Total Revenue", cols[4:8]].sum()
                    revenue_growth = (last4 - prev4) / prev4 if prev4 else None

        # 評分
        score = 0
        if eps_growth and eps_growth > 0: score += 1
        if revenue_growth and revenue_growth > 0: score += 1
        if gross_margin and gross_margin > 0.3: score += 1
        if pe and 10 <= pe <= 25: score += 1

        if score <= 1:
            level = "偏弱"
        elif score <= 3:
            level = "中性"
        else:
            level = "優質"

        return {
            "score": score,
            "level": level,
            "pe": round(pe, 2) if pe else None,
            "gross_margin": round(gross_margin * 100, 2) if gross_margin else None,
            "revenue_growth": round(revenue_growth * 100, 2) if revenue_growth else None,
            "eps_growth": round(eps_growth * 100, 2) if eps_growth else None
        }

    except Exception as e:
        print(e)
        return {"score": 0, "level": "未知"}