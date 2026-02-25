from admin_config import *


#? EN: Checks if user has permission to create new chat links and redirects to link creation
#* RU: Проверяет, есть ли у пользователя права на создание новых ссылок для чатов и перенаправляет к созданию ссылки
@router.callback_query(F.data == "new_chat_link_check")
async def new_link_check(call: types.CallbackQuery):
    if call.from_user.id in can_new_link_users:
        await new_link(call)
        return
    else:
        await call.answer(text='⚠️Тебе не доступна эта функция')
        return

#? EN: Shows squad selection menu for creating new chat links (1st or 2nd squad)
#* RU: Показывает меню выбора состава для создания новых ссылок чата (1-й или 2-й состав)
@router.callback_query(F.data == "new_chat_link")
async def new_link(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1 состав", callback_data="1sost"),
        types.InlineKeyboardButton(text="2 состав", callback_data="2sost")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
    await call.message.answer("Создание новой ссылки", reply_markup=keyboard)

#? EN: Shows participant count selection for 1st squad links (1, 2, or 3 people)
#* RU: Показывает выбор количества участников для ссылок 1-го состава (1, 2 или 3 человека)
@router.callback_query(F.data == "1sost")
async def first_sost(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1", callback_data="one1pep"),
        types.InlineKeyboardButton(text="2", callback_data="one2pep"),
        types.InlineKeyboardButton(text="3", callback_data="one3pep")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
    await call.message.answer('На сколько человек расчитана ссылка', reply_markup=keyboard)


#? EN: Shows participant count selection for 2nd squad links (1, 2, or 3 people)
#* RU: Показывает выбор количества участников для ссылок 2-го состава (1, 2 или 3 человека)
@router.callback_query(F.data == "2sost")
async def two_sost(call: types.CallbackQuery):
    await call.message.delete()
    buttons = [
        types.InlineKeyboardButton(text="1", callback_data="two1pep"),
        types.InlineKeyboardButton(text="2", callback_data="two2pep"),
        types.InlineKeyboardButton(text="3", callback_data="two3pep")
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])
    await call.message.answer('На сколько человек расчитана ссылка', reply_markup=keyboard)

#? EN: Creates a single-use link for 1st squad with 1 activation
#* RU: Создаёт одноразовую ссылку для 1-го состава с 1 активацией
@router.callback_query(F.data == "one1pep")
async def one1pep(call: types.CallbackQuery):
    activate_count = 1
    sost = 1
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)', (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}', parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()

#? EN: Creates a link for 1st squad with 2 activations
#* RU: Создаёт ссылку для 1-го состава с 2 активациями
@router.callback_query(F.data == "one2pep")
async def one2pep(call: types.CallbackQuery):
    activate_count = 2
    sost = 1
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


#? EN: Creates a link for 1st squad with 3 activations
#* RU: Создаёт ссылку для 1-го состава с 3 активациями
@router.callback_query(F.data == "one3pep")
async def one3pep(call: types.CallbackQuery):
    activate_count = 3
    sost = 1
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


#? EN: Creates a single-use link for 2nd squad with 1 activation
#* RU: Создаёт одноразовую ссылку для 2-го состава с 1 активацией
@router.callback_query(F.data == "two1pep")
async def two1pep(call: types.CallbackQuery):
    activate_count = 1
    sost = 2
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


#? EN: Creates a link for 2nd squad with 2 activations
#* RU: Создаёт ссылку для 2-го состава с 2 активациями
@router.callback_query(F.data == "two2pep")
async def two2pep(call: types.CallbackQuery):
    activate_count = 2
    sost = 2
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()


#? EN: Creates a link for 2nd squad with 3 activations
#* RU: Создаёт ссылку для 2-го состава с 3 активациями
@router.callback_query(F.data == "two3pep")
async def two3pep(call: types.CallbackQuery):
    activate_count = 3
    sost = 2
    connection = sqlite3.connect(datahelp_path, check_same_thread=False)
    cursor = connection.cursor()
    link = f"WERTY-{password_generator.generate(length=8, chars='ASDFGHJKL12345678')}"
    cursor.execute('INSERT INTO links_for_sosts (link_text, activate_count, sost) VALUES (?, ?, ?)',
                   (link, activate_count, sost))
    await call.message.answer(f'Ссылка: <code>{link}</code>\nКоличество активаций: {activate_count}\nСостав: {sost}',
                              parse_mode='HTML')
    await call.message.delete()
    connection.commit()
    connection.close()

