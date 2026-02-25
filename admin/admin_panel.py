from aiogram.exceptions import TelegramBadRequest
from aiogram import types, Bot, F
from admin_config import router, bot, can_admin_panel, klan, sost_1, sost_2, main_path
import sqlite3

#? EN: Checks if user has admin panel access permissions and redirects to admin panel
#* RU: Проверяет, есть ли у пользователя права доступа к админ-панели и перенаправляет к админ-панели
@router.callback_query(F.data == "admn_panell_check")
async def admn_panell_check(call: types.CallbackQuery, bot: Bot):
    if call.from_user.id in can_admin_panel:
        await admin_panel(call, bot)
        return
    else:
        await bot.answer_callback_query(call.id, text='Тебе не доступна эта функция', show_alert=True)
        return

#? EN: Shows the main admin panel with options to view users and chat permissions
#* RU: Показывает главную админ-панель с опциями просмотра пользователей и разрешений чата
@router.callback_query(F.data == "admn_panel")
async def admin_panel(call: types.CallbackQuery, bot: Bot):
    print(call.from_user.id)
    if call.from_user.id in [1240656726,1401086794,8015726709]:
        pass
    else:
        await bot.answer_callback_query(call.id, text='В разработке', show_alert=True)
        return
    buttons = [
        types.InlineKeyboardButton(text="Участники", callback_data="users"),
        types.InlineKeyboardButton(text="Просмотр дк", callback_data="dk"),
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    await call.message.edit_text( text="Админ панель", reply_markup=keyboard)

#? EN: Shows menu for viewing command permissions (dk) in different chats
#* RU: Показывает меню для просмотра разрешений команд (дк) в разных чатах
@router.callback_query(F.data == "dk")
async def dk_menu(call: types.CallbackQuery, bot: Bot):
    buttons = [
        types.InlineKeyboardButton(text="Клан", callback_data="dk_klan"),
        types.InlineKeyboardButton(text="Cостав", callback_data="dk_sost-1"),
        types.InlineKeyboardButton(text="◀️ Назад", callback_data="admn_panel"),
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    await call.message.edit_text( text="Дк чатов", reply_markup=keyboard)


#? EN: Shows menu for viewing users in different chats (clan, squad 1, squad 2)
#* RU: Показывает меню для просмотра пользователей в разных чатах (клан, 1-й состав, 2-й состав)
@router.callback_query(F.data == "users")
async def users_menu(call: types.CallbackQuery, bot: Bot):
    buttons = [
        types.InlineKeyboardButton(text="Клан", callback_data="all_klan"),
        types.InlineKeyboardButton(text="Первый Cостав", callback_data="all_sost-1"),
        types.InlineKeyboardButton(text="Второй Cостав", callback_data="all_sost-2"),
        types.InlineKeyboardButton(text="◀️ Назад", callback_data="admn_panel"),
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    await call.message.edit_text( text="Юзеры чатов", reply_markup=keyboard)

#? EN: Handles dynamic callbacks for viewing users or command permissions in specific chats
#* RU: Обрабатывает динамические колбэки для просмотра пользователей или разрешений команд в конкретных чатах
@router.callback_query()
async def dk_in_chat(call: types.CallbackQuery, bot: Bot):

    if call.data.split('_')[0] == 'all':
        ids_chats = {
            'klan': klan,
            'sost-1': sost_1,
            'sost-2': sost_2
        }

        a= (ids_chats[call.data.split("_")[1]])
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        users_count_reg = int(cursor.execute(f'SELECT COUNT(*) FROM [{-(a)}]').fetchone()[0]) - 1
        users_count = int(cursor.execute(f'SELECT count FROM count_users WHERE chat_id = ?', (a,)).fetchone()[0])
        print(users_count_reg, users_count)
        cursor.execute(f'SELECT * FROM [{-(a)}]')
        users = cursor.fetchall()
        tg_ids = []
        usernames = []
        names = []
        age = []
        nik_pubg = []
        id_pubg = []
        nik = []
        rang = []
        last_date = []
        date_vhod = []
        mess_count = []
        users_all = []
        user_count = 0
        rangs_name = ('Обычный участник', 'Младший Модератор', 'Модератор', 'Старший Модератор', 'Заместитель', 'Менеджер',
                      'Владелец')

        for user in users:
            tg_ids.append(user[0])
            usernames.append(user[1])
            names.append(user[2])
            age.append(user[3])
            nik_pubg.append(user[4])
            id_pubg.append(user[5])
            nik.append(user[6])
            rang.append(user[7])
            last_date.append(user[8])
            date_vhod.append(user[9])
            mess_count.append(user[10])
            user_count += 1

        for i in range(user_count):
            if usernames[i] == 'all':
                text = ''
            else:
                text = f'<b>{i + 1}.</b> <a href="https://t.me/{usernames[i]}">{nik[i]}</a> (@{usernames[i]}) | <b>Должность:</b> {rangs_name[rang[i]]} <b>[{rang[i]}]</b>'
            users_all.append(text)
        buttons = [
            types.InlineKeyboardButton(text="Клан", callback_data="all_klan"),
            types.InlineKeyboardButton(text="Первый Cостав", callback_data="all_sost-1"),
            types.InlineKeyboardButton(text="Второй Cостав", callback_data="all_sost-2"),
            types.InlineKeyboardButton(text="◀️ Назад", callback_data="users"),
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
        intog = '\n\n'.join(users_all)
        try:
            await call.message.edit_text(text=f"▫️<b>Количество зарегестрированых юзеров:</b> {users_count_reg}\n▫️<b>Количество всех пользователей чата:</b> {users_count}\n\n<b>Пользователи:</b>\n{intog}", parse_mode='HTML', reply_markup=keyboard, disable_web_page_preview=True)
        except TelegramBadRequest:
            await bot.answer_callback_query(call.id, text='Уже на этой странице')
            return

    if call.data.split('_')[0] == 'dk':
        ids_chats = {
            'klan': 'klan',
            'sost-1': 'sostav',
            'sost-2': 'sostav'
        }
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        a = (ids_chats[call.data.split("_")[1]])
        cursor.execute(f'SELECT * FROM [{a}]')
        dks = cursor.fetchall()

        commans = []
        dk = []
        command_count = 0
        itog = []
        for command in dks:
            commans.append(command[0])
            dk.append(command[1])
            command_count += 1


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
        for i in range(command_count):
            text = f'▫️{command_name[commans[i]]}: <b>{dk[i]}</b>'
            itog.append(text)

        buttons = [
            types.InlineKeyboardButton(text="Клан", callback_data="dk_klan"),
            types.InlineKeyboardButton(text="Cостав", callback_data="dk_sost-1"),
            types.InlineKeyboardButton(text="◀️ Назад", callback_data="dk"),
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
        intod = '\n'.join(itog)
        try:
            await call.message.edit_text(text=intod, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)
        except TelegramBadRequest:
            await bot.answer_callback_query(call.id, text='Уже на этой странице')
            return
