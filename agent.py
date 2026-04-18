# agent.py
import time
from tools import get_stock_report
from ai import ask_llm

# 快取（同一標的短時間內不重算）
CACHE = {}
TTL_SEC = 900  # 15分鐘

def _get_cache(key):
    v = CACHE.get(key)
    if not v:
        return None
    data, ts = v
    if time.time() - ts > TTL_SEC:
        return None
    return data

def _set_cache(key, value):
    CACHE[key] = (value, time.time())

def run_agent(ticker: str) -> str:
    # 1) 先看快取
    cached = _get_cache(ticker)
    if cached:
        return cached

    # 2) 數據計算
    data = get_stock_report(ticker)
    if not data:
        return f"❌ 找不到 {ticker} 數據"

    # 3) prompt（控制長度，避免被擋）
    prompt = f"""
標的：{data['id']}（現價 {data['price']}）
24D乖離：{data['bias']:.2f}%
歷史區間：{data['low']:.1f}% ~ {data['high']:.1f}%
狀態：{data['status']}

用「資深量化操盤手」語氣，120字內：
1. 判斷目前水位
2. 給具體策略（買/觀望/減碼）
"""

    # 4) 呼叫 AI
    ai_text = ask_llm(prompt)

    # 5) 組合輸出
    report = (
        f"📊 {data['id']} 戰略診斷\n"
        f"━━━━━━━━━━━━\n"
        f"💰 現價：{data['price']}\n"
        f"📈 乖離：{data['bias']:.2f}%\n"
        f"📏 區間：{data['low']:.1f}% ~ {data['high']:.1f}%\n"
        f"🚩 狀態：{data['status']}\n\n"
        f"🤖 操盤手：\n{ai_text}"
    )

    # 6) 寫入快取
    _set_cache(ticker, report)

    return report