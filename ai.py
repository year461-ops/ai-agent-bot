import os
import google.generativeai as genai
from dotenv import load_dotenv # 修正 1: 確保載入環境變數

# 讀取 .env 檔案中的金鑰
load_dotenv()

# 修正 2: 設定 API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def ask_llm(prompt):
    try:
        # 修正 3: 使用更加穩定的模型名稱名稱
        # 如果 "gemini-1.5-flash" 報 404，通常改用 "gemini-1.5-flash-latest" 就能解決
        # 或者嘗試使用 2.0 版本: "gemini-2.0-flash"
        model = genai.GenerativeModel("gemini-1.5-flash-latest")

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 300 # 稍微放寬 token 限制
            }
        )

        # 安全檢查
        if res and hasattr(res, 'text'):
            return res.text
        
        # 處理安全過濾
        if hasattr(res, 'candidates') and res.candidates:
            return "AI 內容被屏蔽（可能涉及敏感資訊）"

        return "AI 無回應"

    except Exception as e:
        # 這裡會噴出具體的錯誤原因
        error_msg = str(e)
        if "404" in error_msg:
            return f"AI錯誤: 找不到模型，請嘗試將模型名稱改為 gemini-2.0-flash"
        return f"AI錯誤: {error_msg}"