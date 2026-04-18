import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. 載入環境變數
load_dotenv()

# 2. 配置 API Key (確保 .env 裡有 GEMINI_API_KEY)
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def ask_llm(prompt):
    try:
        # 3. 2026 年核心模型：Gemini 2.0 Flash
        # 此模型在 2026 年具備最佳的反應速度與金融數據理解力
        model = genai.GenerativeModel("gemini-2.0-flash")

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 400
            }
        )

        # 4. 回傳解析結果
        if res and hasattr(res, 'text'):
            return res.text
        
        return "AI 暫時無法回覆，請檢查輸入數據是否正常。"

    except Exception as e:
        error_msg = str(e)
        # 自動識別常見錯誤
        if "404" in error_msg:
            return "AI錯誤: 找不到模型路徑，請嘗試更新 SDK (pip install -U google-generativeai)。"
        if "429" in error_msg:
            return "AI錯誤: 請求過於頻繁 (Quota Exceeded)，請稍後再試。"
        return f"AI錯誤: {error_msg}"