import os
import telebot
import threading
from flask import Flask
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ========================
# Flask 保活（Railway必備）
# ========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

def run_web():
    app.run(host="0.0.0.0", port=8080)

# ========================
# Telegram 指令
# ========================
@bot.message_handler(commands=['ask'])
def handle_ask(message):
    parts = message.text.split()

    if len(parts) < 2:
        bot.reply_to(message, "請輸入 /ask 股票代碼")
        return

    ticker = parts[1].upper()

    msg = bot.reply_to(message, f"分析 {ticker} 中...")

    result = run_agent(ticker)

    bot.edit_message_text(
        result,
        chat_id=message.chat.id,
        message_id=msg.message_id
    )

# ========================
# 啟動
# ========================
if __name__ == "__main__":
    print("🚀 Bot 啟動中（含 Web Server）")

    # 🔥 開 Web（Railway需要）
    threading.Thread(target=run_web).start()

    # 🔥 跑 Telegram
    bot.infinity_polling()