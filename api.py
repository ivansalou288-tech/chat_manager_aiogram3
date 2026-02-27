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

class SnatWarnAction(BaseModel):
    chat: str
    userid: str
    num: int

class BanAction(BaseModel):
    chat: str
    userid: str
    reason: str


chats_names = {'klan': 1002143434937, 'sost-1': 1002274082016, 'sost-2': 1002439682589}

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


async def get_users_sdk(chat: str):
       
    connection = sqlite3.connect(main_path)
    cursor = connection.cursor()
    userss = cursor.execute(f'SELECT * FROM [{chats_names[chat]}]').fetchall()
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

            # Пытаемся получить статус участника в чате; если его больше нет в чате,
            # Telegram может вернуть ошибку "member not found" — тогда считаем, что
            # пользователь не состоит в чате.
            try:
                chat_member = await bot.get_chat_member(-(chats_names[chat]), tg_ids)
                status = chat_member.status
            except Exception:
                status = 'left'

            if status == 'administrator':
                chat_status = '👨🏻‍🔧 Телеграм-админ этого чата'
            elif status == 'creator':
                chat_status = '👨🏻‍🔧 Создатель этого чата'
            elif status == 'member' or status == 'restricted':
                chat_status = '💚 Состоит в чате'
            else:
                chat_status = '💔 Не состоит в чате'

            users[index] = {
                'tg_ids': tg_ids,
                'username': usernames,
                'name': names,
                'age': age,
                'nik_pubg': nik_pubg,
                'id_pubg': id_pubg,
                'nik': nik,
                'rang': rang,
                'last_date': last_date,
                'date_vhod': date_vhod,
                'mess_count': mess_count,
                'status': chat_status,
            }
            index += 1
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
        await snat_admn_warn(user_id, 3, 2, chats_names[chat])
        await snat_admn_warn(user_id, 2, 1, chats_names[chat])
        await snat_admn_warn(user_id, 1, 0, chats_names[chat])
        message_idd = (await bot.send_message(-(chats_names[chat]), f'<b>{voscl}Внимание{voscl}</b>\n{circle_em}Злостный нарушитель {user_men} получает бан и покидает нас\n👮‍♂️Выгнал его: Некий админ\n{mes_em}Выгнали его за: {reason}', parse_mode='html')).message_id
        await insert_ban_user(user_id, user_men, 'Admin Panel', reason, message_idd, -(chats_names[chat]))
        await bot.ban_chat_member(-(chats_names[chat]), user_id)

def dell_sdk(chat_id: int, user_id: int) -> Any:
        
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        cursor.execute(f'DELETE FROM [{chat_id}] WHERE tg_id = ?', (user_id, ))
        connection.commit()
    except sqlite3.OperationalError:
        pass

    connection.commit()

def full_dell_sdk(user_id: int) -> Any:
        
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    for chat_id in chats_names.values():
        try:
            cursor.execute(f'DELETE FROM [{chat_id}] WHERE tg_id = ?', (user_id, ))
            connection.commit()
        except sqlite3.OperationalError:
            pass

    connection.commit()


async def admin_warn_dell(user_id: int, chat_id: int, number_warn: int, new_warns_count: int): #Удаляет нужное предупреждение с сообщением в чат 
    await snat_admn_warn(user_id, number_warn, new_warns_count, chat_id)
    mention = GetUserByID(user_id).mention
    await bot.send_message(chat_id=-(chat_id), text=f'{mention}, с тебя сняли одно предупреждение\n👮‍♂️Добрый модер: Некий админ\n{mes_em} Количество твоих предупреждений: {new_warns_count} из 3\n\n<i>Свои предупреждения ты можешь посмотреть по команде</i> «<code>преды</code>»', parse_mode='html')

@app.get("/users/{chat}")
async def get_users(chat: str):
    if chat in chats_names.keys():
        users = await get_users_sdk(chat)
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

@app.get('/recom/{user}')
def get_recom(user: int):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    all = cursor.execute('SELECT * FROM recommendation WHERE user_id = ?', (user,)).fetchall()
    recomendations = []
    for rec in all:
        print(rec)
        id = rec[0]
        pubg_id = rec[1]
        moder_id = rec[2]
        reason = rec[3]
        rang = rec[4]
        date = rec[5]
        rec_id = rec[6]
        recom = {"id": id,
                 "pubg_id": pubg_id,
                 "moder_id": moder_id,
                 "reason": reason,
                 "rang": rang,
                 "date": date,
                 "rec_id": rec_id,
                 }
        recomendations.append(recom)
    return recomendations


@app.get('/warns/{chat}/{user}')
def get_warns(chat: str, user: int):
    chat_id = chats_names.get(chat)
    if chat_id is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM [{(chat_id)}] WHERE tg_id=?", (user,))
    row = cursor.fetchone()

    # Если предупреждений нет — возвращаем пустой список
    if not row:
        return []

    # Структура строки берётся из snat_admn_warn:
    # 0: tg_id, 1: warns_count, 2: first_warn, 3: second_warn, 4: therd_warn,
    # 5: first_moder, 6: second_moder, 7: therd_moder
    first_warn, second_warn, therd_warn = row[2], row[3], row[4]
    first_moder, second_moder, therd_moder = row[5], row[6], row[7]

    warns = []
    if first_warn:
        warns.append({"num": 1, "reason": first_warn, "moder": first_moder})
    if second_warn:
        warns.append({"num": 2, "reason": second_warn, "moder": second_moder})
    if therd_warn:
        warns.append({"num": 3, "reason": therd_warn, "moder": therd_moder})

    # Вернём максимум 3 предупреждения (по факту их и так максимум 3)
    return warns[:3]



@app.post("/ban")
async def ban(action: BanAction):
    chat = action.chat
    userid = action.userid
    reason = action.reason
    print(f'b {chat} {userid} {reason}')
    await admin_ban(chat, int(userid), reason)
    return {"status": "ok"}

@app.post("/dell")
def dell(action: UserAction):
    chat = action.chat
    userid = action.userid
    print(f'd {chat} {userid}')
    chat_id = chats[chat]
    dell_sdk(chat_id, userid)
    return {"status": "ok"}

@app.post("/full_dell")
def full_dell(action: UserAction):
    chat = action.chat
    userid = action.userid
    print(f'fd {chat} {userid}')
    full_dell_sdk(userid)
    return {"status": "ok"}



@app.post("/snat_warn")
async def snat_warn(action: SnatWarnAction):
    chat = action.chat
    userid = action.userid
    num = action.num
    connection = sqlite3.connect(warn_path, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(f"SELECT warns_count FROM [{(chats_names[chat])}] WHERE tg_id=?", (userid,))
    row = cursor.fetchone()
    cnt = row[0] if row else 0

    await admin_warn_dell(int(userid), chats_names[chat], num, max(cnt - 1, 0))
    return {"status": "ok"}

if  __name__ == '__main__':
    uvicorn.run('api:app', reload=True, host="0.0.0.0")
    
    