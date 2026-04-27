from tools import get_stock_report, get_fundamental_score
from ai import ask_ai

def run_agent(ticker):
    data = get_stock_report(ticker)

    if not data:
        return f"❌ 找不到 {ticker} 的資料"

    fund = get_fundamental_score(ticker)

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

🧠 技術評分：{data['score']}/4 → {decision}

🎯 操作區間
支撐：{data['support']}
壓力：{data['resistance']}
"""

    report += f"""
📊 基本面分析
━━━━━━━━━━━━
評分：{fund['score']}/4 → {fund['level']}
P/E：{fund.get('pe', 'N/A')}
毛利率：{fund.get('gross_margin', 'N/A')}%
營收成長：{fund.get('revenue_growth', 'N/A')}%
EPS成長：{fund.get('eps_growth', 'N/A')}%
"""

    ai_text = ask_ai(data)

    return report + "\n🤖 AI建議：\n" + ai_text