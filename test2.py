import google.generativeai as genai

genai.configure(api_key="AIzaSyCDnEYVPPz6s8z3FpENR7iWuTBAZNmCHo8")

print("🔍 正在掃描你的 API Key 可用的模型...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 可用名稱: {m.name}")
except Exception as e:
    print(f"❌ 掃描失敗: {e}")