# ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_llm(prompt):

    # 直接用 1.5（穩定 + 快）
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        res = model.generate_content(prompt)

        if res and res.text:
            return res.text

    except Exception as e:
        return f"1.5錯誤: {str(e)}"

    return "AI 無回應"