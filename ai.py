# ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_llm(prompt):
    try:
        # 🔥 直接用穩定模型（不卡）
        model = genai.GenerativeModel("gemini-1.5-flash")

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "max_output_tokens": 200
            }
        )

        if res and res.text:
            return res.text

        return "AI 無回應"

    except Exception as e:
        return f"AI錯誤: {str(e)}"