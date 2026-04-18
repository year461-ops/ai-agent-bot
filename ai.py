# ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-1.5-flash"  # ← 改這個

def ask_llm(prompt):
    try:
        model = genai.GenerativeModel(MODEL_NAME)

        response = model.generate_content(prompt)

        if response and response.text:
            return response.text

        return "AI 無回應"

    except Exception as e:
        return f"Gemini錯誤：{str(e)}"