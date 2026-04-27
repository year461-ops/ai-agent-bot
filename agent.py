from tools import get_stock_report
from ai import ask_ai

def run_agent(ticker):
    data = get_stock_report(ticker)

    if not data:
        return f"❌ 找不到 {ticker} 的近期有效資料"

    # ========================
    # 評分解讀
    # ========================
    if data["score"] <= 1:
        decision = "觀望"
    elif data["score"] <= 3:
        decision = "可布局"
    else:
        decision = "強烈訊號"

    report = f"""
📊 {data['id']} 戰略分析
━━━━━━━━━━━━
💰 現價：{data['price']}
📈 乖離：{data['bias']}%
📏 區間：{data['low']}% ~ {data['high']}%
📊 RSI：{data['rsi']}
📉 趨勢：{data['trend']}
📦 量能：{data['volume_ratio']}倍
🚩 狀態：{data['status']}

🧠 綜合評分：{data['score']}/4 → {decision}

🎯 操作區間
支撐：{data['support']}
壓力：{data['resistance']}
"""

    ai_text = ask_ai(data)

    return report + "\n🤖 AI建議：\n" + ai_text