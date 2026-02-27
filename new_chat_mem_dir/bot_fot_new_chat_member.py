import random
import time
import types
from datetime import datetime
from unittest.mock import call
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import prinatie_token as token
import sqlite3
import telebot
from path import Path
from telebot.types import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup

curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'



connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()



logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])
print(logs_gr, sost_1, sost_2, klan)
bot = telebot.TeleBot(token)

is_in_clan = False

#? EN: Generates and sends clan and squad invite links to the user based on their assigned squad
#* RU: Генерирует и отправляет ссылки-приглашения в клан и состав пользователю на основе назначенного состава
def links(message, sostav):
    connection = sqlite3.connect(dinamik_path, check_same_thread=False)
    cursor = connection.cursor()
    if sostav == 1:
        klan_link = bot.export_chat_invite_link(klan)
        sostav_link =  bot.export_chat_invite_link(sost_1)


    elif sostav == 2:
        klan_link = bot.export_chat_invite_link(klan)
        sostav_link = bot.export_chat_invite_link(sost_2)

    bot.send_message(message.chat.id, klan_link)
    bot.send_message(message.chat.id, sostav_link)
    cursor.execute('DELETE FROM is_to_klan WHERE user_id = ?', (message.from_user.id,))
    connection.commit()
    

#? EN: Sends step-by-step guide with images on how to join the clan in PUBG game
#* RU: Отправляет пошаговое руководство с изображениями о том, как вступить в клан в игре PUBG
def gaid(message):
    id_copy = CopyTextButton(text=str(51445023900))

    id_btn = InlineKeyboardButton(text="📋Скопировать айди Лидера",
                                        copy_text=id_copy)  # Внедряем текст для копирования в инлайн-кнопки

    keyboard = InlineKeyboardMarkup().add(id_btn)
    bot.send_message(chat_id=message.chat.id,
                     text='Как вступить в клан?\n\n<b>1.</b> Ищешь игрока wePiKAcHy по айди «<code>51445023900</code>» и нажимаешь на его аватарку',
                     parse_mode='html', reply_markup=keyboard)
    bot.send_media_group(chat_id=message.chat.id, media=[telebot.types.InputMediaPhoto(open(f'{curent_path}/photos/first_step.jpg', 'rb')), telebot.types.InputMediaPhoto(open(
        f'{curent_path}/photos/second_step.jpg', 'rb'))])
    bot.send_message(chat_id=message.chat.id,
                     text='<b>2.</b> В его профиле нажимаешь на аватарку клана «Werty» и в всплышем окне нажимаешь на запрос',
                     parse_mode='html')
    bot.send_media_group(chat_id=message.chat.id,
                         media=[telebot.types.InputMediaPhoto(open(f'{curent_path}/photos/therd_step.jpg', 'rb')),
                                telebot.types.InputMediaPhoto(open(f'{curent_path}/photos/last_step.jpg', 'rb'))])



#? EN: Handles /start command and shows main menu with options to join clan or indicate existing membership
#* RU: Обрабатывает команду /start и показывает главное меню с опциями вступления в клан или указания существующего членства
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != message.from_user.id:
        return
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except telebot.apihelper.ApiTelegramException:
        pass
    buttons = [
        telebot.types.InlineKeyboardButton(text="Вступить в клан", callback_data="new_member"),
        telebot.types.InlineKeyboardButton(text="Уже в клане", callback_data="not_new"),
        telebot.types.InlineKeyboardButton(text='Посмотреть канал Werty', url="https://t.me/Werty_Metro")


    ]
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    bot.send_photo(chat_id=message.chat.id, photo=open(f'{curent_path}/photos/klan_ava.jpg', 'rb'), reply_markup=keyboard, caption='Приветствуем тебя в нашем боте!\nЧто ты хочешь сделать?')


#? EN: Handles callback queries from inline buttons - processes new member registration or existing member confirmation
#* RU: Обрабатывает колбэк-запросы от инлайн-кнопок - обрабатывает регистрацию нового участника или подтверждение существующего участника
@bot.callback_query_handler(func=lambda call: True)
def new_member(call):
    if call.data == "not_new":
        # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text='Ты уже в клане! тебе не нужно не куда входить, иди сопровождения делай)')
    if call.data == "new_member":
        # bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text = 'Напишите ваш код вступления')
        global is_in_clan
        is_in_clan = True

#? EN: Handles photo messages from users who completed clan joining process and sends them invite links
#* RU: Обрабатывает фото-сообщения от пользователей, завершивших процесс вступления в клан, и отправляет им ссылки-приглашения
@bot.message_handler(content_types=['photo'])
def get_media(message):
    if message.chat.id != message.from_user.id:
        return
    connection = sqlite3.connect(dinamik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        tg_id = cursor.execute('SELECT sostav FROM is_to_klan WHERE user_id = ?',(message.from_user.id, )).fetchall()[0][0]
    except IndexError:
        return
    links(message, tg_id)

#? EN: Processes text messages containing entry codes and starts the clan registration process
#* RU: Обрабатывает текстовые сообщения, содержащие коды вступления, и запускает процесс регистрации в клан
@bot.message_handler()
def get_text_messages(message):

    if message.chat.id != message.from_user.id:
        return


    global is_in_clan
    if is_in_clan == False:
        return
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT activate_count, sost FROM links_for_sosts WHERE link_text = ?", (message.text,))
    except sqlite3.OperationalError:
        bot.send_message(chat_id=message.chat.id, text = 'Ошибка баззы данных, поробуйте позже')
        return
    link_data = cursor.fetchall()
    connection.commit()
    if link_data == []:
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except telebot.apihelper.ApiTelegramException:
            pass
        bot.send_message(chat_id=message.chat.id, text='Неверный код вступления, за новым обратитесь к @werty_pub')
        return
    activate_count, sostav = link_data[0]
    activate_count_new = activate_count - 1
    if activate_count_new == 0:
        cursor.execute('DELETE FROM links_for_sosts WHERE link_text = ?', (message.text,))
        connection.commit()
        connection.close()
    else:
        cursor.execute('UPDATE links_for_sosts SET activate_count = ? WHERE link_text = ?', (activate_count_new, message.text))
        connection.commit()
        connection.close()




    #? EN: Checks if user is already registered in the clan database
    #* RU: Проверяет, зарегистрирован ли пользователь в базе данных клана
    def firstSeen(get_id):
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute(f"SELECT tg_id FROM [{-klan}] WHERE tg_id=?", (get_id,))
        rez = cursor.fetchall()

        if not rez:
            print("add")
            # addUser(get_id)

            return True
        else:
            print('Уже в базе')
            # cursor.execute('UPDATE users SET name, age, nik_pubg, id_pubg = ?, ?, ?, ? WHERE tg_id = ?', (name, age, id_pubg, nik_pubg, get_id))
            return False

    if not firstSeen(message.chat.id):
        bot.send_message(message.chat.id, 'Вы уже участник клана!')
    else:
        print(f'{message.from_user.id} входит в клан')


        #? EN: Processes user's name input during registration
        #* RU: Обрабатывает ввод имени пользователя во время регистрации
        def name(message):
            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()

            name = message.text
            cursor.execute('UPDATE din_reg SET name = ? WHERE tg_id = ?',
                           (name, message.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except telebot.apihelper.ApiTelegramException:
                pass
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши свой возраст:')
            bot.register_next_step_handler(msg, aget)

        #? EN: Processes and validates user's age input during registration
        #* RU: Обрабатывает и проверяет ввод возраста пользователя во время регистрации
        def aget(message):


            try:
                age = int(message.text)
            except ValueError:
                msg = bot.send_message(chat_id=message.chat.id, text='Возраст должен быть одним числом\nНапиши свой возраст:')
                bot.register_next_step_handler(msg, aget)
                return
            if age < 7 or age > 50:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Напиши свой реальный возраст!\nНапиши свой возраст:')
                bot.register_next_step_handler(msg, aget)
                return
            cursor.execute('UPDATE din_reg SET age = ? WHERE tg_id = ?',
                           (age, message.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except telebot.apihelper.ApiTelegramException:
                pass
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши свой игровой айди:')
            bot.register_next_step_handler(msg, id_pubgt)

        #? EN: Processes and validates user's PUBG ID input during registration
        #* RU: Обрабатывает и проверяет ввод PUBG ID пользователя во время регистрации
        def id_pubgt(message):

            try:
                id_pubg = int(message.text)
            except ValueError:
                msg = bot.send_message(chat_id=message.chat.id,
                                       text='Айди должно быть одним числом\nНапиши свое айди:')
                bot.register_next_step_handler(msg, id_pubgt)
                return

            #? EN: Splits a number into individual digits for validation
            #* RU: Разбивает число на отдельные цифры для проверки
            def split_number(number):
                num = []
                while number > 0:
                    digit = number % 10
                    num.append(digit)
                    number = number // 10
                return num[::-1]


            id_p = split_number(id_pubg)
            if id_p[0] != 5 or len(str(id_pubg)) < 9 or len(str(id_pubg)) > 12:
                msg = bot.send_message(chat_id=message.chat.id, text = 'Айди некореткное!\nВведите коректное игровое айди:')
                bot.register_next_step_handler(msg, id_pubgt)
                return
            cursor.execute('UPDATE din_reg SET id_pubg = ? WHERE tg_id = ?',
                           (id_pubg, message.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except telebot.apihelper.ApiTelegramException:
                pass
            msg = bot.send_message(message.chat.id, 'Принято! теперь напиши игровой ник:')
            bot.register_next_step_handler(msg, nik_pubg)

        #? EN: Processes user's PUBG nickname input and completes registration
        #* RU: Обрабатывает ввод PUBG никнейма пользователя и завершает регистрацию
        def nik_pubg(message):

            nik_pubg = message.text
            cursor.execute('UPDATE din_reg SET nik_pubg = ? WHERE tg_id = ?',
                           (nik_pubg, message.from_user.id))
            connection.commit()
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
            except telebot.apihelper.ApiTelegramException:
                pass

            #функция кидания ссылок на клан, состав, и правил
            addUser(message.from_user.id, message.from_user.username)

        #? EN: Adds the new user to clan and squad databases and sends welcome message with instructions
        #* RU: Добавляет нового пользователя в базы данных клана и состава и отправляет приветственное сообщение с инструкциями
        def addUser(tg_id, username):

            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM din_reg WHERE tg_id = ?', (tg_id,))
            users = cursor.fetchall()

            for user in users:
                user_about = {
                    'tg_id': user[0],
                    'username': user[1],
                    'name': user[2],
                    'age': user[3],
                    'nik_pubg': user[4],
                    'id_pubg': user[5],
                    'nik': user[6],
                    'rang': user[7],
                    'last_date': user[8],
                    'date_vhod': user[9],
                }
            connection.commit()
            connection.close()
            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()
            now = datetime.now().strftime('%H:%M:%S %d.%m.%Y')
            cursor.execute(f'INSERT INTO [{-klan}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (tg_id, username, user_about['name'], user_about['age'], user_about['nik_pubg'], user_about['id_pubg'], user_about['nik_pubg'], 0, '', now))
            connection.commit()
            connection.close()
            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute('DELETE FROM din_reg WHERE tg_id = ?', (message.from_user.id,))
            connection.commit()
            connection.close()

            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()
            try:
                cursor.execute(f'INSERT INTO all_users (user_id, username) VALUES (?, ?)', (tg_id, username))
                connection.commit()
            except sqlite3.IntegrityError:
                connection.commit()
                cursor.execute(f'UPDATE all_users SET username = ? WHERE user_id = ?', (username, tg_id))
                connection.commit()
            connection.commit()
            if sostav == 1:
                # klan_link = bot.export_chat_invite_link(klan)
                # sostav_link =  bot.export_chat_invite_link(sost_1)
                try:
                    cursor.execute(
                        f'INSERT INTO [{-sost_1}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (tg_id, username, user_about['name'], user_about['age'], user_about['nik_pubg'],
                        user_about['id_pubg'], user_about['nik_pubg'], 0, '', now))
                except Exception:
                    pass
                connection.commit()

            elif sostav == 2:
                # klan_link = bot.export_chat_invite_link(klan)
                # sostav_link = bot.export_chat_invite_link(sost_2)
                try:
                    cursor.execute(
                        f'INSERT INTO [{-sost_2}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (tg_id, username, user_about['name'], user_about['age'], user_about['nik_pubg'],
                         user_about['id_pubg'], user_about['nik_pubg'], 0, '', now))
                except Exception:
                    pass
                connection.commit()


            else:
                bot.send_message(message.chat.id,
                                 f"Твое описание:\nИмя: {user_about['name']}\nВозраст: {user_about['age']}\nАйди: {user_about['id_pubg']}\nНик: {user_about['nik_pubg']}")
                bot.send_message(logs_gr,
                                 f' <a href="tg://user?id={message.chat.id}">Пользователь</a> вошел в клан и {sostav} состав\n\nЕго описание: \nИмя: {user_about["name"]}\nВозраст: {user_about["age"]}\nАйди: {user_about["id_pubg"]}\nНик: {user_about["nik_pubg"]}',
                                 parse_mode='html')
                # cursor.execute(
                #     f'INSERT INTO [{-sost_2}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                #     (tg_id, username, user_about['name'], user_about['age'], user_about['nik_pubg'],
                #      user_about['id_pubg'], user_about['nik_pubg'], 0, '', now))
                # connection.commit()
                try:
                    cursor.execute(
                        f'INSERT INTO [{-sost_1}] (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (tg_id, username, user_about['name'], user_about['age'], user_about['nik_pubg'],
                         user_about['id_pubg'], user_about['nik_pubg'], 0, '', now))
                except Exception:
                    pass
                connection.commit()
                connection.close()
                print('successful')
                return
            connection = sqlite3.connect(main_path, check_same_thread=False)
            cursor = connection.cursor()
            try:
                cursor.execute('INSERT INTO black_list (user_id, rison) VALUES (?, ?)', (tg_id, ''))
            except Exception:
                pass
            connection.commit()  
            bot.send_message(message.chat.id,
                             f'Добро пожаловать в клан Werty!\n\nТвое описание:\nИмя: {user_about["name"]}\nВозраст: {user_about["age"]}\nАйди: {user_about["id_pubg"]}\nНик: {user_about["nik_pubg"]}\n\n Твои ссылки на состав и клан:')
            time.sleep(0.5)
            bot.send_message(message.chat.id, f"!!Ознакомься!!\n\n{cursor.execute('SELECT text FROM texts WHERE text_name = ?', ('pravils',)).fetchall()[0][0]}")
            gaid(message)
            time.sleep(0.5)
            bot.send_photo(chat_id=message.chat.id, photo=open(f'{curent_path}/photos/is_klan.jpg', 'rb'),caption=f"После того как ты ознакомился с информацией выше, кинь скрин того как ты кинул в клан")
            time.sleep(0.5)
            
            
            bot.send_message(logs_gr,
                             f' <a href="https://t.me/{user_about["username"]}">Пользователь</a> вошел в клан и {sostav} состав\n\nЕго описание: \nИмя: {user_about["name"]}\nВозраст: {user_about["age"]}\nАйди: {user_about["id_pubg"]}\nНик: {user_about["nik_pubg"]}',
                             parse_mode='html')
            connection.commit()
            connection.close()


            connection = sqlite3.connect(dinamik_path, check_same_thread=False)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO is_to_klan (user_id, sostav) VALUES (?, ?)', (tg_id, sostav))
            connection.commit()







        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            cursor.execute(
                f'INSERT INTO din_reg (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (message.from_user.id, message.from_user.username, '', 0, '', random.randint(0,1000000000), '', 0, '', 0))
            connection.commit()
        except sqlite3.IntegrityError:
            cursor.execute('DELETE FROM din_reg WHERE tg_id = ?', (message.from_user.id,))
            cursor.execute(
                f'INSERT INTO din_reg (tg_id, username, name, age, nik_pubg, id_pubg, nik, rang, last_date, date_vhod) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (message.from_user.id, message.from_user.username, '', 0, '', random.randint(0, 1000000000), '', 0, '',
                 0))
            connection.commit()
        msg = bot.send_message(message.chat.id, 'Напиши свое имя:')
        bot.register_next_step_handler(msg, name)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        except telebot.apihelper.ApiTelegramException:
            pass

def main():
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(e)
        time.sleep(1)
        main()


if __name__ == "__main__":
    main()





