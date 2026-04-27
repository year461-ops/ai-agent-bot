def ask_ai(data):
    import os
    import google.generativeai as genai
    from dotenv import load_dotenv

    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    MODELS = [
        "gemini-2.5-flash",
        "gemini-3-flash",
        "gemini-2.5-flash-lite"
    ]

    prompt = f"""
股票：{data['id']}
現價：{data['price']}
乖離率：{data['bias']}%
區間：{data['low']}% ~ {data['high']}%
RSI：{data['rsi']}
趨勢：{data['trend']}
量能：{data['volume_ratio']}倍
狀態：{data['status']}

請用專業交易員角度分析，內容包含：
1. 現在是否適合進場
2. 風險與可能走勢
3. 短線操作建議（含觀望/布局/減碼）
4. 關鍵觀察重點

請用條列式，約100~150字
"""

    for model in MODELS:
        try:
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"{model} error: {e}")
            continue

    return "AI暫時無法分析"