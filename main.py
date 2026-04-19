# main.py
import os
import telebot
import logging
from dotenv import load_dotenv
from agent import run_agent

# ===== 基本設定 =====
load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("❌ TELEGRAM_TOKEN 未設定")

bot = telebot.TeleBot(TOKEN)

# ===== /ask 指令 =====
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    try:
        text = message.text.strip()

        # 解析指令（支援群組 /ask@botname）
        parts = text.split()

        if len(parts) < 2:
            bot.reply_to(message, "請輸入股票代碼，例如：/ask 2330")
            return

        ticker = parts[1].strip().upper()

        msg = bot.reply_to(message, f"分析 {ticker} 中...")

        result = run_agent(ticker)

        bot.edit_message_text(
            result,
            chat_id=message.chat.id,
            message_id=msg.message_id
        )

    except Exception as e:
        logging.error(f"錯誤: {e}")
        bot.reply_to(message, f"❌ 發生錯誤：{e}")

# ===== 啟動 =====
if __name__ == "__main__":
    print("🤖 Bot 啟動中...")
    bot.infinity_polling()