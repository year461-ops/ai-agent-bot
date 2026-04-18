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

# 2. 終極模型兵器譜 (過濾掉 0/0 與非文字模型，按推薦順序排列)
MODELS_TO_TRY = [
    # --- 第一梯隊：Gemini Flash 主力 (聰明且支援長文本) ---
    "gemini-2.5-flash",       # 限額: 5 RPM
    "gemini-3-flash",         # 限額: 5 RPM
    
    # --- 第二梯隊：Gemini Flash Lite (速度極快) ---
    "gemini-3.1-flash-lite",  # 限額: 15 RPM
    "gemini-2.5-flash-lite",  # 限額: 10 RPM
    
    # --- 第三梯隊：Gemma 開源家族 (作為最後防線) ---
    # 注意：呼叫 Gemma 文字生成模型通常需要加上 -it (Instruct) 後綴
    "gemma-4-31b-it",         # 限額: 15 RPM
    "gemma-4-26b-it",         # 限額: 15 RPM
    "gemma-3-27b-it",         # 限額: 30 RPM
    "gemma-3-12b-it"          # 限額: 30 RPM
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
            
            # 遇到 429 流量限制
            if "429" in error_msg or "Quota" in error_msg:
                print(f"  ⚠️ {model_name} 額度已滿，切換下一個！")
                continue
                
            # 遇到 404 (有些 Gemma 模型端點名稱可能在 API 中有微調)
            elif "404" in error_msg or "not found" in error_msg.lower():
                print(f"  ⚠️ 找不到 {model_name} 端點，跳過。")
                continue
                
            # 其他未知錯誤也直接跳過，確保程式絕對不死機
            else:
                print(f"  ❌ {model_name} 發生錯誤: {error_msg}，切換下一個！")
                continue

    # 如果這 8 個模型全部都被榨乾了 (總共破百次請求)
    print("  ⏳ 整個 AI Studio 的免費模型都在冷卻中，強制暫停 60 秒...")
    time.sleep(60)
    
    print("  🔄 冷卻完畢，從頭再來！")
    return generate_with_infinite_fallback(prompt_text)

# ==========================================
# 實際測試區塊 
# ==========================================
if __name__ == "__main__":
    print("--- 啟動終極榨汁機：全模型接力模式 ---")
    
    # 故意執行 15 次，這絕對會跨越單一模型 5 RPM 的限制，觸發接力機制
    for i in range(1, 16): 
        print(f"\n▶️ 開始處理第 {i} 筆任務")
        
        # 測試用的 Prompt 
        test_prompt = f"任務編號 {i}：請簡述在評核臺北一、臺中、臺南，一路到臺東門市的服務品質時，巡檢報告最常出現的一項缺失。"
        
        result = generate_with_infinite_fallback(test_prompt)
        
        # 為了版面乾淨，只印出前 30 個字來確認成功
        print(f"  ✅ 成功取得回應：{result[:30]}...")
        
        time.sleep(1) 
        
    print("\n🎉 所有任務處理完畢，完全沒有中斷！")