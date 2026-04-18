from tools import get_stock_report
from ai import generate_with_infinite_fallback # 🎯 關鍵：把你的接力函式 import 進來

def run_agent(ticker):
    # 1. 先去 tools.py 抓技術指標資料
    data = get_stock_report(ticker)
    
    if not data:
        return f"❌ 找不到 {ticker} 的近期有效資料，請確認代碼是否正確。"

    # 2. 組合出你要發送給 AI 的戰略報告版型
    report_text = f"""📊 {data['id']} 戰略診斷
━━━━━━━━━━━━
💰 現價：{data['price']}
📈 乖離：{data['bias']}%
📏 區間：{data['low']}% ~ {data['high']}%
🚩 狀態：{data['status']}
"""

    # 3. 組合 Prompt (告訴 AI 它該做什麼)
    prompt = f"""
    以下是股市資料：
    {report_text}
    
    請以「資深操盤手」的語氣，根據上述乖離率與狀態，給出 50 字以內的精準操作建議，直接輸出建議文字即可。
    """

    # 4. 🚀 將 Prompt 丟給你的「無限接力榨汁機」處理
    ai_advice = generate_with_infinite_fallback(prompt)

    # 5. 將原本的數據和 AI 的分析拼在一起，回傳給 main.py 去發 Telegram
    final_output = f"{report_text}\n🤖 操盤手：\n{ai_advice}"
    
    return final_output