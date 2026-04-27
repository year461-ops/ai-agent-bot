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
📊 RSI：{data['rsi']}
📉 趨勢：{data['trend']}
📦 量能：{data['volume_ratio']}倍
🚩 狀態：{data['status']}

🧠 技術評分：{data['score']}/4 → {decision}
"""

    report += f"""
📊 基本面分析
━━━━━━━━━━━━
評分：{fund['score']}/4 → {fund['level']}
P/E：{fund['pe'] if fund['pe'] else '無資料'}
毛利率：{fund['gross_margin'] if fund['gross_margin'] else '無資料'}%
營收成長：{fund['revenue_growth'] if fund['revenue_growth'] else '無資料'}%
EPS成長：{fund['eps_growth'] if fund['eps_growth'] else '無資料'}%
"""

    ai_text = ask_ai(data)

    return report + "\n🤖 AI建議：\n" + ai_text