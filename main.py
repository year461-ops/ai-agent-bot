# main.py
import os
import telebot
from agent import run_agent

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    text = message.text.replace("/ask", "").strip()

    if not text:
        bot.reply_to(message, "請輸入股票代碼")
        return

    msg = bot.reply_to(message, "分析中...")

    result = run_agent(text)

    bot.edit_message_text(
        result,
        chat_id=message.chat.id,
        message_id=msg.message_id
    )


# ===== 自動掃描（Agent主動行動）=====
import threading
import time

WATCHLIST = ["2330", "NVDA", "AAPL"]

def auto_scan():
    while True:
        for t in WATCHLIST:
            result = run_agent(t)

            if "🔥" in result or "⚠️" in result:
                bot.send_message(os.getenv("GROUP_CHAT_ID"), result)

        time.sleep(300)  # 5分鐘


if __name__ == "__main__":
    threading.Thread(target=auto_scan).start()
    bot.infinity_polling()