def ask_ai_strategy(data):
    prompt = f"""
    你是專精於「異常管理」的半導體戰略顧問。
    標的代碼：{data['id']} (現價: {data['price']})
    目前 24D 乖離率：{data['bias']:.2f}%
    歷史定義極限區間：{data['low']:.1f}% 到 {data['high']:.1f}%
    診斷狀態：{data['status']}
    
    請提供 120 字內的戰略建議，包含當前水位判定與具體行動指令。
    用繁體中文，專業且精確。
    """
    try:
        # 加入安全設定，避免 AI 判定投資建議為敏感內容而拒答
        response = ai_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.7)
        )
        # 確保有回傳內容
        if response.candidates:
            return response.text
        else:
            return "AI 判定此標的內容敏感，無法給予建議。"
    except Exception as e:
        # 這行會把真正的錯誤噴在你的電腦螢幕上，請截圖給我看
        print(f"❌ Gemini API 發生錯誤: {e}") 
        return "Gemini 分析器目前忙碌中，請查看終端機錯誤訊息。"