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

def ask_ai(data):
    prompt = f"""
股票：{data['id']}
乖離率：{data['bias']}%
區間：{data['low']}% ~ {data['high']}%
狀態：{data['status']}

請用專業語氣給出交易建議（50字內）
"""

    for model in MODELS:
        try:
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"{model} error: {e}")
            continue

    return "AI暫時無法分析"