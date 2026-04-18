import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_llm(prompt):
    try:
        model = genai.GenerativeModel("models/gemini-flash-latest")

        res = model.generate_content(prompt)

        if res and res.text:
            return res.text

        return "AI 無回應"

    except Exception as e:
        return f"AI錯誤: {str(e)}"