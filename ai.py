import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 載入 .env 中的金鑰
load_dotenv()

# 2. 設定 API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def ask_llm(prompt):
    try:
        # 3. 使用目前最穩定的模型名稱
        # 2026 年建議直接使用名稱，不加 "models/"
        model = genai.GenerativeModel("gemini-1.5-flash")

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 400
            }
        )

        # 4. 回傳文字，若被安全過濾則回傳提示
        if res and hasattr(res, 'text'):
            return res.text
        
        return "AI 內容被屏蔽或未生成文字，請檢查輸入內容。"

    except Exception as e:
        error_msg = str(e)
        # 針對 404 錯誤的自動修復建議
        if "404" in error_msg:
            return "AI錯誤: 找不到模型。請於終端機執行 'pip install -U google-generativeai'。"
        return f"AI錯誤: {error_msg}"