import os
import time
from google import genai
from dotenv import load_dotenv

# 1. 安全載入金鑰
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("找不到 GEMINI_API_KEY，請檢查 .env 檔案！")

client = genai.Client(api_key=api_key)

# 2. 終極模型兵器譜
MODELS_TO_TRY = [
    # --- 第一梯隊：主力 ---
    "gemini-2.5-flash",       
    "gemini-3-flash",         
    
    # --- 第二梯隊：極速 ---
    "gemini-3.1-flash-lite",  
    "gemini-2.5-flash-lite",  
    
    # --- 第三梯隊：開源無限 ---
    "gemma-4-31b-it",         
    "gemma-4-26b-it",         
    "gemma-3-27b-it",         
    "gemma-3-12b-it"          
]

def generate_with_infinite_fallback(prompt_text):
    """
    貫穿全部可用模型的終極接力函式
    """
    for model_name in MODELS_TO_TRY:
        try:
            print(f"  🤖 嘗試呼叫 {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text
            )
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Quota" in error_msg:
                print(f"  ⚠️ {model_name} 額度已滿，切換下一個！")
                continue
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"  ⚠️ 找不到 {model_name} 端點，跳過。")
                continue
            else:
                print(f"  ❌ {model_name} 發生錯誤: {error_msg}，切換下一個！")
                continue

    # 萬一全部榨乾，休息 60 秒後重啟
    print("  ⏳ 所有免費模型冷卻中，強制暫停 60 秒...")
    time.sleep(60)
    print("  🔄 冷卻完畢，從頭再來！")
    return generate_with_infinite_fallback(prompt_text)