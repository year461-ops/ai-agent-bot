# ai.py
import os
import time
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODELS = [
    "models/gemini-2.5-flash",
    "models/gemini-2.5-flash-lite",
    "gemini-1.5-flash"
]

# 簡單冷卻（避免 429 連發）
_last_call = 0
COOLDOWN_SEC = 5

def _cooldown():
    global _last_call
    now = time.time()
    delta = now - _last_call
    if delta < COOLDOWN_SEC:
        time.sleep(COOLDOWN_SEC - delta)
    _last_call = time.time()

def ask_llm(prompt: str) -> str:
    _cooldown()

    last_err = None
    for name in MODELS:
        try:
            model = genai.GenerativeModel(name)
            res = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.6,
                    "max_output_tokens": 220
                }
            )
            if res and getattr(res, "text", None):
                return res.text
        except Exception as e:
            msg = str(e)
            last_err = msg

            # 命中配額就等一下再試下一個
            if "429" in msg:
                time.sleep(45)
                continue
            # 模型/權限問題直接換下一個
            if "not found" in msg or "permission" in msg:
                continue
            # 其他錯誤也換下一個
            continue

    return f"❌ AI失敗：{last_err}"