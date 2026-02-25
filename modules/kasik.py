import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
from aiogram import Router, types, F

import asyncio
import sqlite3


from main.config3 import *
from path import Path

# Create router for message and callback handlers
router = Router()

curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'
kasik_path = curent_path / 'databases' / 'kasik.db'



#? EN: Opens the casino (slot/dice) interface, letting user choose a bet from their farm bag with cooldown.
#* RU: Открывает интерфейс казика (слоты/кости), позволяя выбрать ставку из мешка фармы с кулдауном.
@router.message(F.text.in_(['!казик', '! казик']))
async def kasik(message: types.Message):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])


    #  if message.from_user.id != 1240656726:
    #     return
    if message.chat.id == message.from_user.id:
        await message.answer(
            '📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!')
        return
    if message.chat.id not in chats:
        await message.answer('кыш')
        return
    
    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        period_str = cursor.execute('SELECT period FROM default_periods WHERE command = ? AND chat = ?', ('kasik', message.chat.id)).fetchall()[0][0]
        time_value, time_unit = period_str.split()
        time_value = int(time_value)
        if time_unit in ['ч', 'час', 'часа', 'часов']:
            cd_delta = timedelta(hours=time_value)
        elif time_unit in ['мин', 'минут', 'минута', 'минуты']:
            cd_delta = timedelta(minutes=time_value)
        elif time_unit in ['д', 'день', 'дня', 'дней', 'сутки']:
            cd_delta = timedelta(days=time_value)
        else:
            cd_delta = timedelta(minutes=15)
    except (IndexError, ValueError):
        cd_delta = timedelta(minutes=15)

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = message.from_user.id
    try:
        cursor.execute(f"SELECT last_date FROM stavki WHERE user_id = ?", (user_id,))
        lst = datetime.strptime(cursor.fetchall()[0][0], "%H:%M:%S %d.%m.%Y")
        now = datetime.now()
        delta = now - lst
        if delta > cd_delta:
            pass
        else:
            delta = cd_delta - delta
            days = delta.days * 24
            sec = int(str(delta.total_seconds()).split('.')[0])

            hours = sec // 3600 - days
            minutes = (sec % 3600) // 60
            days = delta.days

            if days == 0:
                days_text = ''
            else:
                days_text = f'{days} дн '
            if hours == 0:
                hours_text = ''
            else:
                hours_text = f'{hours} ч '
            if minutes == 0:
                minutes_text = ''
            else:
                minutes_text = f'{minutes} мин '

            lst_date = f'{days_text}{hours_text}{minutes_text}'
            await message.answer(f'❌Можно играть в казик только раз в {period_str}. Следующий деп через {lst_date}', parse_mode='html')
            return
    except IndexError:
        pass

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    user_id = message.from_user.id
    try:
        meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchall()[0][0]
    except IndexError:
        await message.answer('Твой мешок пустой! Иди работай а потом депай')
        return
    if int(meshok)<100:
        await message.answer('Твой мешок пустой! Иди работай а потом депай')
        return
    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    stavka = 100
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    message_id = (await message.bot.send_photo(message.chat.id, photo=FSInputFile(f'{curent_path}/photos/dep.jpg'), caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka}', parse_mode='html', reply_markup=keyboard)).message_id
    try:
        cursor.execute('INSERT INTO stavki (user_id, mess_id, stavka, last_date) VALUES (?, ?, ?, ?)', (user_id, message_id, 100,  datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
        connection.commit()
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE stavki SET stavka = ? WHERE user_id = ?', (100, user_id))
        connection.commit()
        cursor.execute('UPDATE stavki SET mess_id = ? WHERE user_id = ?', (message_id, user_id))
        connection.commit()
        cursor.execute('UPDATE stavki SET last_date = ? WHERE user_id = ?', (datetime.now().strftime("%H:%M:%S %d.%m.%Y"), user_id))
        connection.commit()
    connection.commit()


#? EN: Increases the casino bet by 1000 eZ¢ (if user has enough coins).
#* RU: Увеличивает ставку в казике на 1000 eZ¢ (если у пользователя хватает монет).
@router.callback_query(F.data == 'plus1')
async def plus_1k(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+1000) > int(meshok):
        await call.bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+1000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+1000}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 1000 eZ¢ but not below the minimum (100).
#* RU: Уменьшает ставку в казике на 1000 eZ¢, но не ниже минимальной (100).
@router.callback_query(F.data == 'minus1')
async def minus_1k(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-1000) < 100:
        await call.bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-1000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-1000}', parse_mode='html', reply_markup=keyboard)

#? EN: Increases the casino bet by 10 000 eZ¢ (big step).
#* RU: Увеличивает ставку в казике на 10 000 eZ¢ (крупный шаг).
@router.callback_query(F.data == 'plus5')
async def plus_10k(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+10000) > int(meshok):
        await call.bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+10000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+10000}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 10 000 eZ¢ but not below 100.
#* RU: Уменьшает ставку в казике на 10 000 eZ¢, но не ниже 100.
@router.callback_query(F.data == 'minus5')
async def minus_10k(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-10000) < 100:
        await call.bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-10000 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [a, b],
        [f, g],
        [t, y],
        [d],
        [c]
    ])

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-10000}', parse_mode='html', reply_markup=keyboard)



#? EN: Increases the casino bet by 100 eZ¢ (small step).
#* RU: Увеличивает ставку в казике на 100 eZ¢ (малый шаг).
@router.callback_query(F.data == 'plus')
async def plus_100(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)+100) > int(meshok):
        await call.bot.answer_callback_query(call.id, text='У тебя нет столько деняг!')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka+100 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka+100}', parse_mode='html', reply_markup=keyboard)


#? EN: Decreases the casino bet by 100 eZ¢ but not below 100.
#* RU: Уменьшает ставку в казике на 100 eZ¢, но не ниже 100.
@router.callback_query(F.data == 'minus')
async def minus_100(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    if (int(stavka)-100) < 100:
        await call.bot.answer_callback_query(call.id, text='Ставка не может быть меньше 100')
        return
    cursor.execute('UPDATE stavki SET stavka = stavka-100 WHERE user_id = ?', (call.from_user.id,))
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)

    await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {stavka-100}', parse_mode='html', reply_markup=keyboard)

#? EN: Sets the casino bet to the user’s entire bag balance (All-In).
#* RU: Устанавливает ставку в казике равной всему балансу мешка пользователя (All-In).
@router.callback_query(F.data == 'all_in')
async def all_in(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?', (call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return
    connection.commit()
    a = InlineKeyboardButton(text="+100", callback_data="plus")
    b = InlineKeyboardButton(text="-100", callback_data="minus")
    f = InlineKeyboardButton(text="+1000", callback_data="plus1")
    g = InlineKeyboardButton(text="-1000", callback_data="minus1")
    t = InlineKeyboardButton(text="+10k", callback_data="plus5")
    y = InlineKeyboardButton(text="-10k", callback_data="minus5")
    c = InlineKeyboardButton(text="🎰Депнуть", callback_data="dep")
    d = InlineKeyboardButton(text="💀All-In", callback_data="all_in")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.add(a, b).add(f,g).add(t,y).row(d).row(c)
    try:
        await call.message.edit_caption(caption=f'💰 В твоем мешке: 🍊 {meshok}  eZ¢\nТвоя ставка: {meshok}', parse_mode='html', reply_markup=keyboard)
    except Exception:
        return


#? EN: Rolls Telegram dice, resolves the casino game and updates user’s bag based on win/lose result.
#* RU: Бросает телеграм‑кубик, определяет исход игры в казике и обновляет мешок пользователя по результату.
@router.callback_query(F.data == 'dep')
async def dep(call: types.CallbackQuery):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    meshok = cursor.execute(f"SELECT meshok FROM farma WHERE user_id = ?", (call.from_user.id,)).fetchall()[0][0]

    connection = sqlite3.connect(kasik_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        stavka = cursor.execute('SELECT stavka FROM stavki WHERE user_id = ? AND mess_id = ?',(call.from_user.id, call.message.message_id)).fetchall()[0][0]
    except IndexError:
        await call.bot.answer_callback_query(call.id, text='Не для тебя кнопку создавали')
        return

    res = (await call.bot.send_dice(call.message.chat.id)).dice.value
    await call.message.delete()
    if res <=4:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)-int(stavka), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await call.bot.send_photo(call.message.chat.id, photo=FSInputFile(f'{curent_path}/photos/proig.jpg'), caption=f'Ты проиграл! повезет в следущий раз! \n\n💰 В твоем мешке теперь: 🍊 {int(meshok)-int(stavka)}  eZ¢\nТвоя ставка: {stavka}', parse_mode='html')
    if res == 5:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)+int(stavka), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await call.bot.send_photo(call.message.chat.id, photo=FSInputFile(f'{curent_path}/photos/win.jpg'), caption=f'🎉Ты выиграл! И получил Х2 к своей ставке\n💰 В твоем мешке теперь: 🍊 {int(meshok)+int(stavka)}  eZ¢\n🎄Твоя ставка: {stavka}', parse_mode='html')

    if res == 6:
        await asyncio.sleep(3)
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        cursor.execute('UPDATE farma SET meshok = ? WHERE user_id = ?', (int(meshok)+(2 * int(stavka)), call.from_user.id))
        connection.commit()
        connection = sqlite3.connect(kasik_path, check_same_thread=False)
        cursor = connection.cursor()
        # cursor.execute('DELETE FROM stavki WHERE user_id = ?', (call.from_user.id,))
        connection.commit()
        await call.bot.send_photo(call.message.chat.id, photo=FSInputFile(f'{curent_path}/photos/win.jpg'), caption=f'🎉Ты выиграл! И получил Х3 к своей ставке\n💰 В твоем мешке теперь: 🍊 {int(meshok)+2*(int(stavka))}  eZ¢\n🎄Твоя ставка: {stavka}', parse_mode='html')

# Note: Router should be included in main bot setup
# Add this router to your dispatcher: dp.include_router(router)