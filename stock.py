import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

def get_66_strategy_status(stock_id):
    # --- 1. 資料抓取 ---
    ticker = f"{stock_id}.TW"
    # 增加 period 確保有足夠的資料量計算 60MA
    df = yf.download(ticker, period="3mo", interval="1h", progress=False)
    
    if df.empty or len(df) < 60:
        ticker = f"{stock_id}.TWO"
        df = yf.download(ticker, period="3mo", interval="1h", progress=False)
    
    if df.empty or len(df) < 60:
        return f"❌ 無法獲取股票 {stock_id} 的足夠資料。"

    # --- 關鍵修正：攤平 MultiIndex 欄位 ---
    # 新版 yfinance 會回傳像 ('Close', '2451.TW') 這樣的組合，我們要把它簡化回 'Close'
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # --- 2. 計算指標 (加上安全檢查) ---
    try:
        # 計算 60MA
        df['MA60'] = ta.sma(df['Close'], length=60)
        
        # 計算 KD (6, 3, 3)
        # 確保傳入的是 Series，且移除可能導致計算失敗的 NaN
        kd_df = ta.stoch(high=df['High'], low=df['Low'], close=df['Close'], k=6, d=3, smooth_k=3)
        
        if kd_df is None:
            return "❌ KD 指標計算失敗，請檢查資料完整性 (可能有缺漏值)。"
            
        df['K'] = kd_df['STOCHk_6_3_3']
        df['D'] = kd_df['STOCHd_6_3_3']
    except Exception as e:
        return f"❌ 計算過程中發生錯誤: {str(e)}"

    # --- 3. 資料補償邏輯 ---
    df = df.dropna(subset=['MA60', 'K']) # 確保只看有數值的列
    if len(df) < 2:
        return "❌ 運算後有效資料不足，建議更換標的或稍後再試。"

    confirmed_bar = df.iloc[-2]
    current_bar = df.iloc[-1]

    def is_buy_signal(row):
        return (row['Close'] > row['MA60']) and (row['K'] > 60)

    conf_signal = is_buy_signal(confirmed_bar)
    curr_signal = is_buy_signal(current_bar)

    # --- 4. 輸出報告 ---
    report = [
        f"--- 66 戰法掃描報告 ({datetime.now().strftime('%H:%M:%S')}) ---",
        f"標的代號: {ticker}",
        f"當前價格: {current_bar['Close']:.2f} (MA60: {current_bar['MA60']:.2f})",
        f"當前 K 值: {current_bar['K']:.2f}",
        "-------------------------------------------"
    ]

    if conf_signal and curr_signal:
        report.append("🔥 買進訊號：【強力站穩】前一小時已確認，動能持續！")
    elif not conf_signal and curr_signal:
        report.append("⚡ 買進訊號：【即時發動】剛衝過基準線，建議等收盤確認。")
    elif conf_signal and not curr_signal:
        report.append("⚠️ 警訊：【動能回檔】原本站穩但目前小時跌破，不建議追高。")
    else:
        report.append("💤 觀望：目前不符合 66 戰法條件。")
    
    return "\n".join(report)

if __name__ == "__main__":
    stock_code = input("請輸入台股代號 (如 2330): ").strip()
    result = get_66_strategy_status(stock_code)
    print(result)