import sqlite3
import os
import sys
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import asyncio
from datetime import datetime
# Добавляем корневую директорию проекта в путь
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

from main.config3 import *
import main.secret
TOKEN = main.secret.main_token

bot = Bot(token=TOKEN)
class UserAction(BaseModel):
    chat: str
    userid: str

class BanAction(BaseModel):
    chat: str
    userid: str
    reason: str


chats = {'klan': 1002143434937, 'sost-1': 1002274082016, 'sost-2': 1002439682589}

command_name = {
            'ban': 'Блокировка пользователей',
            'mut': 'Ограничение пользователей',
            'warn': 'Предупреждение пользователей',
            'all': 'Созыв пользователей',
            'rang': 'Изменение ранга пользователей',
            'dk': 'Изменение доступа вызова команд',
            'change_pravils': 'Изменение правил чата',
            'close_chat': 'Изменение ограничений чата',
            'change_priv': 'Изменение приветствия чата',
            'obavlenie': 'Создание объявления',
            'tur': 'Создание турниров',
            'dell': 'Удаление сообщений',
            'period': 'Изменение периодов'
        }

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_users_sdk(chat: str):
       
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    userss = cursor.execute(f'SELECT * FROM [{chats[chat]}]').fetchall()
    users = {}
    index = 1
    for user in userss:
            
            tg_ids = user[0]
            usernames = user[1]
            names = user[2]
            age = user[3]
            nik_pubg = user[4]
            id_pubg = user[5]
            nik = user[6]
            rang = user[7]
            last_date = user[8]
            date_vhod = user[9]
            mess_count = user[10]
            users[index] = {'tg_ids': tg_ids, 'username': usernames, 'name': names, 'age': age, 'nik_pubg': nik_pubg, 'id_pubg': id_pubg, 'nik': nik, 'rang': rang, 'last_date': last_date, 'date_vhod': date_vhod, 'mess_count': mess_count}
            index +=1
    return users

def get_dk_sdk(chat: str):

    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM [{chat}]')
    dks = cursor.fetchall()
    dkss = {}
    index = 1
    for dk in dks:
         command = dk[0]
         access = dk[1]
         index+=1
         dkss[index] = {'command': command_name[command], 'access': access}
         
    return dkss


async def snat_admn_warn(user_id, number_warn, warn_count_new, chat_id):
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    num_list = ['nul', 'first', 'second', 'therd']
    number_warn_dell = f'{num_list[number_warn]}_warn'
    number_moder = f'{num_list[number_warn]}_moder'
    try:
        text = cursor.execute(f'SELECT {number_warn_dell} FROM [{(chat_id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    except IndexError:
        return
    moder = cursor.execute(f'SELECT {number_moder} FROM [{(chat_id)}] WHERE tg_id = ?', (user_id,)).fetchall()[0][0]
    cursor.execute(f'UPDATE [{(chat_id)}] SET warns_count = ? WHERE tg_id = ?',
                   (warn_count_new, user_id))
    connection.commit()
    cursor.execute(f'UPDATE [{(chat_id)}] SET {number_warn_dell} = ? WHERE tg_id = ?',
                   (None, user_id))
    connection.commit()
    cursor.execute(f"SELECT * FROM [{(chat_id)}] WHERE tg_id=?", (user_id,))
    connection.commit()
    warns = cursor.fetchall()[0]

    first_warn = warns[2]
    second_warn = warns[3]
    therd_warn = warns[4]
    first_mod = warns[5]
    second_mod = warns[6]
    therd_mod = warns[7]

    if number_warn == 1:
        first_warn = second_warn
        second_warn = therd_warn
        therd_warn = None
        first_mod = second_mod
        second_mod = therd_mod
        therd_mod = None
    if number_warn == 2:
        second_warn = therd_warn
        therd_warn = None
        second_mod = therd_mod
        therd_mod = None
    number_warn_dell = f'{num_list[number_warn]}_warn'
    cursor.execute(f'UPDATE [{(chat_id)}] SET first_warn = ? WHERE tg_id = ?',
                   (first_warn, user_id))
    cursor.execute(f'UPDATE [{(chat_id)}] SET second_warn = ? WHERE tg_id = ?',
                   (second_warn, user_id))
    cursor.execute(f'UPDATE [{(chat_id)}] SET therd_warn = ? WHERE tg_id = ?',(therd_warn, user_id))
    cursor.execute(f'UPDATE [{(chat_id)}] SET first_moder = ? WHERE tg_id = ?',
                   (first_mod, user_id))
    cursor.execute(f'UPDATE [{(chat_id)}] SET second_moder = ? WHERE tg_id = ?',
                   (second_mod, user_id))
    cursor.execute(f'UPDATE [{(chat_id)}] SET therd_moder = ? WHERE tg_id = ?',
                   (therd_mod, user_id))
    connection.commit()

    cursor.execute(f'INSERT INTO [{(chat_id)}snat] (user_id, warn_text, moder_give, moder_snat) VALUES (?, ?, ?, ?)', (user_id, text, moder, 'Admin Panel'))
    connection.commit()
    cursor.execute(f'DELETE FROM [{(chat_id)}snat] WHERE moder_give IS NULL AND warn_text IS NULL')
    connection.commit()

async def insert_ban_user(user_id, user_men, moder_men, comments, message_id, chat_id):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        pubg_id = cursor.execute(f"SELECT id_pubg FROM [{-(chat_id)}] WHERE tg_id=?", (user_id,)).fetchall()[0][0]
    except IndexError:
        pubg_id = 'неизвестен'
    date = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
    try:
        cursor.execute(f'INSERT INTO [{-(chat_id)}bans] (tg_id, id_pubg, message_id, prichina, date, user_men, moder_men) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, pubg_id, message_id, comments, date, user_men, moder_men))
    except sqlite3.IntegrityError:
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET id_pubg = ? WHERE tg_id = ?', (pubg_id, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET message_id = ? WHERE tg_id = ?', (message_id, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET prichina = ? WHERE tg_id = ?', (comments, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET date = ? WHERE tg_id = ?', (date, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET user_men = ? WHERE tg_id = ?', (user_men, user_id))
        cursor.execute(f'UPDATE [{-(chat_id)}bans] SET moder_men = ? WHERE tg_id = ?', (moder_men, user_id))
    connection.commit()
    try:
        cursor.execute(f'DELETE FROM [{-(chat_id)}] WHERE tg_id = ?', (user_id, ))
        connection.commit()
    except sqlite3.OperationalError:
        pass

    connection.commit()

async def admin_ban(chat: str, user_id: int, reason: str | None) -> any:

        user_men = GetUserByID(user_id).mention
        await snat_admn_warn(user_id, 3, 2, chats[chat])
        await snat_admn_warn(user_id, 2, 1, chats[chat])
        await snat_admn_warn(user_id, 1, 0, chats[chat])
        message_idd = (await bot.send_message(-(chats[chat]), f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель {user_men} получает бан и покидает нас\n👮‍♂️Выгнал его: Некий админ\n{mes_em}Выгнали его за: {reason}', parse_mode='html')).message_id
        await insert_ban_user(user_id, user_men, 'Admin Panel', reason, message_idd, -(chats[chat]))
        await bot.ban_chat_member(-(chats[chat]), user_id)


@app.get("/users/{chat}")
def get_users(chat: str):
    if chat in chats.keys():
        users = get_users_sdk(chat)
        return users
    else:
        raise HTTPException(status_code=404, detail="Chat not found")
    
@app.get("/dks/{chat}")
def get_dks(chat: str):
    if chat in ['klan', 'sostav']:
        dkss = get_dk_sdk(chat)
        return dkss
    else:
        raise HTTPException(status_code=404, detail="Chat not found")

@app.post("/ban")
def ban(action: BanAction):
    chat = action.chat
    userid = action.userid
    reason = action.reason
    print(f'b {chat} {userid} {reason}')
    asyncio.run(admin_ban(chat, userid, reason))
    return {"status": "ok"}

@app.post("/dell")
def dell(action: UserAction):
    chat = action.chat
    userid = action.userid
    print(f'd {chat} {userid}')
    return {"status": "ok"}

@app.post("/full_dell")
def full_dell(action: UserAction):
    chat = action.chat
    userid = action.userid
    print(f'fd {chat} {userid}')
    return {"status": "ok"}



if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True)
    
    