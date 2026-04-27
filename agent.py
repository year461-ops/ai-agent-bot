from tools import get_stock_report
from ai import ask_ai   # ✅ 改這行

def run_agent(ticker):
    data = get_stock_report(ticker)

    if not data:
        return f"❌ 找不到 {ticker} 的近期有效資料"

    report = f"""
📊 {data['id']} 戰略診斷
━━━━━━━━━━━━
💰 現價：{data['price']}
📈 乖離：{data['bias']}%
📏 區間：{data['low']}% ~ {data['high']}%
🚩 狀態：{data['status']}
"""

    # ✅ 改這行
    ai_text = ask_ai(data)

    return report + "\n🤖 操盤手：\n" + ai_text