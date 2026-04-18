import os
import google.generativeai as genai

# 建議顯式指定版本
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_llm(prompt):
    try:
        # 改用更明確的模型名稱
        # 2026 年建議優先使用 gemini-1.5-flash 或最新的 gemini-1.5-flash-latest
        model = genai.GenerativeModel("gemini-1.5-flash")

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 200
            }
        )

        # 增加安全檢查，確保 res.text 存在
        if res and hasattr(res, 'text'):
            return res.text
        
        # 處理可能的安全過濾（內容被屏蔽時 text 會報錯）
        if res.candidates:
            return "AI 內容被屏蔽或未生成有效文字"

        return "AI 無回應"

    except Exception as e:
        # 提供更詳細的錯誤資訊方便除錯
        return f"AI錯誤: {str(e)}"