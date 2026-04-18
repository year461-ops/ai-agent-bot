# agent.py
import json
from tools import get_stock_report
from ai import ask_llm

def decide_action(user_input):
    prompt = f"""
    你是量化交易AI Agent

    可用工具：
    - get_stock(ticker)

    使用者輸入：{user_input}

    請輸出JSON：
    {{
        "action": "get_stock 或 final",
        "ticker": "股票代碼或空"
    }}
    """

    res = ask_llm(prompt)

    try:
        return json.loads(res)
    except:
        return {"action": "final", "response": res}


def analyze_stock(data):
    prompt = f"""
    股票：{data['ticker']}
    現價：{data['price']}
    乖離：{data['bias']:.2f}%
    區間：{data['low']:.2f} ~ {data['high']:.2f}
    狀態：{data['status']}

    用專業量化語氣給120字內策略
    """
    return ask_llm(prompt)


def run_agent(user_input):
    decision = decide_action(user_input)

    if decision["action"] == "get_stock":
        data = get_stock_report(decision["ticker"])

        if not data:
            return "❌ 查無資料"

        return analyze_stock(data)

    return decision.get("response", "無法判斷")