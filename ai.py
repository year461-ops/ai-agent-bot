# ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash"

def ask_llm(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(prompt)

        if not response:
            return "❌ 沒有 response（可能被擋）"

        if not hasattr(response, "text"):
            return f"❌ 沒有 text 欄位: {response}"

        return response.text

    except Exception as e:
        return f"🔥 Gemini錯誤：{str(e)}"