from tools import get_stock_report
from ai import generate_with_infinite_fallback # 🎯 引入剛剛寫好的接力函式

def run_agent(ticker):
    # 1. 去 tools.py 算技術指標
    data = get_stock_report(ticker)
    
    if not data:
        return f"❌ 找不到 {ticker} 的近期有效資料，請確認代碼是否正確。"

    # 2. 組合基本數據版面
    report_text = f"""📊 {data['id']} 戰略診斷
━━━━━━━━━━━━
💰 現價：{data['price']}
📈 乖離：{data['bias']}%
📏 區間：{data['low']}% ~ {data['high']}%
🚩 狀態：{data['status']}
"""

    # 3. 寫給 AI 看的 Prompt
    prompt = f"""
    以下是股市資料：
    {report_text}
    
    請以「資深操盤手」的語氣，根據上述乖離率與狀態，給出 50 字以內的精準操作建議，直接輸出建議文字即可。
    """

    # 4. 把 Prompt 丟給 ai.py 去跑接力賽
    ai_advice = generate_with_infinite_fallback(prompt)

    # 5. 把原始數據跟 AI 的建議組合在一起回傳
    final_output = f"{report_text}\n🤖 操盤手：\n{ai_advice}"
    
    return final_output