import telebot
import google.generativeai as genai
import pandas as pd
import time
from datetime import datetime, timedelta
from FinMind.data import DataLoader
from yahooquery import Ticker as YQTicker
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ==========================================
# 🔧 核心配置區 (數據對位完成)
# ==========================================
SYSTEM_NAME = "全球科技 AI 量化雷達" # <--- 在這裡修改你的系統名稱
TELEGRAM_TOKEN = "8604408924:AAFDIhFyiMpSZ5KnzqW7JgTDf4SY9i6PJxA"
GEMINI_API_KEY = "AIzaSyCDnEYVPPz6s8z3FpENR7iWuTBAZNmCHo8"
GROUP_CHAT_ID = "-1003968728718" 

# 使用你掃描到的正確模型名稱
TARGET_MODEL = 'models/gemini-2.5-flash'

print(f"🚀 {SYSTEM_NAME} 正在初始化...")

# 1. 啟動 Telegram 機器人
try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    print(f"✅ Telegram 機器人介接成功")
except Exception as e:
    print(f"❌ Telegram 錯誤: {e}"); exit()

# 2. 啟動 Gemini AI (操盤手人設)
try:
    genai.configure(api_key=GEMINI_API_KEY)
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    ai_model = genai.GenerativeModel(model_name=TARGET_MODEL, safety_settings=safety_settings)
    print(f"✅ {TARGET_MODEL} 大腦連線成功！")
except Exception as e:
    print(f"❌ Gemini 連線失敗: {e}"); exit()

# 3. 啟動數據庫
dl = DataLoader()

# ==========================================
# 🧠 數據引擎：量化乖離率計算
# ==========================================
def get_stock_report(ticker):
    try:
        # 台股 logic
        if ticker.isdigit():
            start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
            df = dl.taiwan_stock_daily(stock_id=ticker, start_date=start_date)
            if df.empty: return None
            df = df.rename(columns={'close': 'Close'}).sort_values('date')
            df['Close'] = pd.to_numeric(df['Close'])
        # 美股 logic
        else:
            q = YQTicker(ticker)
            hist = q.history(period='2y', interval='1d')
            if hist.empty: return None
            df = hist.reset_index().rename(columns={'adjclose': 'Close', 'adj_close': 'Close', 'close': 'Close'})

        close_price = df['Close']
        ma24 = close_price.rolling(window=24).mean()
        bias = (close_price - ma24) / ma24 * 100
        curr_bias = float(bias.iloc[-1])
        
        # 統計極限區間 (5% & 95% 百分位)
        low, high = float(bias.quantile(0.05)), float(bias.quantile(0.95))
        
        status = "⚪ 常態分佈"
        if curr_bias <= low: status = "🔥 超跌買點"
        elif curr_bias >= high: status = "⚠️ 超買警戒"

        return {
            "id": ticker, "bias": curr_bias, "low": low, "high": high, 
            "status": status, "price": float(close_price.iloc[-1])
        }
    except Exception as e:
        print(f"數據計算錯誤: {e}"); return None

# ==========================================
# 🤖 AI 引擎：量化點評
# ==========================================
def ask_ai_strategy(data):
    prompt = f"""
    標的代碼：{data['id']} (現價: {data['price']})
    目前 24D 乖離率：{data['bias']:.2f}%
    歷史極限區間：{data['low']:.1f}% 到 {data['high']:.1f}%
    目前狀態：{data['status']}
    
    請以「資深量化操盤手」視角提供 120 字內短評：
    1. 判定目前股價距離歷史極端水位的位置。
    2. 給予這檔股票目前的具體交易戰略。
    繁體中文，語氣專業、不廢話。
    """
    try:
        response = ai_model.generate_content(prompt)
        return response.text if response.text else "AI 暫時無法分析。"
    except Exception as e:
        return f"AI 點評忙碌中 ({str(e)[:50]})"

# ==========================================
# 📡 Telegram 指令監聽 (/ask)
# ==========================================
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "💡 *請輸入代碼：* `/ask 2330` 或 `/ask NVDA`", parse_mode="Markdown")
            return
            
        ticker = parts[1].upper()
        sent_msg = bot.reply_to(message, f"🔎 正在啟動 {SYSTEM_NAME} 診斷 `{ticker}`...")
        
        data = get_stock_report(ticker)
        if not data:
            bot.edit_message_text(f"❌ 找不到 `{ticker}` 數據。", chat_id=message.chat.id, message_id=sent_msg.message_id)
            return
            
        ai_insight = ask_ai_strategy(data)
        
        report = (
            f"📊 *{data['id']} 戰略診斷報告*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💰 現價：`${data['price']}`\n"
            f"📈 乖離：`{data['bias']:.2f}%`\n"
            f"📏 區間：`{data['low']:.1f}%` ~ `{data['high']:.1f}%`\n"
            f"🚩 狀態：*{data['status']}*\n\n"
            f"🤖 *AI 操盤手點評：*\n{ai_insight}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"📡 {SYSTEM_NAME} | `{datetime.now().strftime('%H:%M')}`"
        )
        bot.edit_message_text(report, chat_id=message.chat.id, message_id=sent_msg.message_id, parse_mode="Markdown")
        
    except Exception as e:
        print(f"錯誤: {e}")

# ==========================================
# 🏃 啟動與廣播
# ==========================================
if __name__ == "__main__":
    print(f"\n📡 {SYSTEM_NAME} 監控中...")
    try:
        bot.send_message(
            GROUP_CHAT_ID, 
            f"🚀 *{SYSTEM_NAME} v2.5 已成功介接！*\n"
            f"當前大腦：`{TARGET_MODEL}`\n"
            "輸入 `/ask 代碼` 即可隨時調閱全球標的分析。"
        )
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ 運行失敗: {e}")