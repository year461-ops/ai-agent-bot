import os
from google import genai
from dotenv import load_dotenv

# 1. 載入 .env 裡的金鑰
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- 2026 Google-GenAI SDK 測試 ---")

try:
    # 2. 初始化 Client (新版 SDK 語法)
    client = genai.Client(api_key=api_key)

    print("正在呼叫 Gemini 1.5 Flash...")
    
    # 3. 發送測試請求
    # 注意：2026 年新版 SDK 不需要 models/ 前綴
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents="你好！如果你收到了這則訊息，請回傳『1.5連線成功』。"
    )

    if response.text:
        print("\n✅ 測試成功！")
        print(f"AI 回應：{response.text}")
    else:
        print("\n⚠️ 有連線但無文字回傳。")

except Exception as e:
    print("\n❌ 測試失敗：")
    print("-" * 30)
    error_msg = str(e)
    print(error_msg)
    print("-" * 30)
    
    # 針對 2026 年常見問題的診斷
    if "404" in error_msg:
        print("💡 診斷：找不到模型。請試著將 model 名稱改為 'gemini-1.5-flash-latest'")
    elif "401" in error_msg or "API_KEY_INVALID" in error_msg:
        print("💡 診斷：API Key 無效。請檢查 .env 檔案內容。")
    elif "429" in error_msg:
        print("💡 診斷：流量過載 (Quota Exceeded)，請等 60 秒再試。")