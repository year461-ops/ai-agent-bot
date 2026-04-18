import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("--- 您的 API Key 目前可使用的模型清單 ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name) # 這裡會輸出像是 models/gemini-3-flash 之類的字串
except Exception as e:
    print(f"查詢出錯: {e}")