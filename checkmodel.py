import google.generativeai as genai

genai.configure(api_key="AIzaSyDRjXQJ7vUXRb_lO5jR2iLDepE8sMtJtnc")  # 先直接寫死測試

models = genai.list_models()

for m in models:
    print(m.name, "→", m.supported_generation_methods)