# main.py
import os
import telebot
from agent import run_agent
import threading
import time

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# ===== /ask =====
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

# ===== 自動掃描（降頻 + 少標的）=====
WATCHLIST = ["2330", "NVDA"]  # 先少量

def auto_scan():
    while True:
        for t in WATCHLIST:
            result = run_agent(t)
            if "🔥" in result or "⚠️" in result:
                bot.send_message(int(os.getenv("GROUP_CHAT_ID")), result)
        time.sleep(1800)  # 30分鐘（避免爆 quota）

if __name__ == "__main__":
    #threading.Thread(target=auto_scan, daemon=True).start()
    bot.infinity_polling()