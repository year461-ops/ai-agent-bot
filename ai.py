# ai.py
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

def ask_llm(prompt):
    try:
        res = model.generate_content(prompt)
        return res.text
    except:
        return "AI error"