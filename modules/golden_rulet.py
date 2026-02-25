import sys
import os
import random
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import types, F, Router, Bot

from aiogram.types import ContentType

from main.config3 import  *
router = Router()

#? EN: Chat command for playing Golden roulette: bets your farm coins, with a chance to lose the bet or double it.
#* RU: Команда чата для игры в Золотую рулетку: ты ставишь коины с фармы с шансом проиграть ставку или удвоить её.
@router.message(F.text.lower().startswith((
            "! золотая рулетка",
            "!золотая рулетка",
            ".золотая рулетка",
            "/золотая рулетка",
            "золотая рулетка",
)) & ~F.is_forwarded,
)
async def golden_roulette(message: types.Message, bot:Bot):
    MUTE_TIME = 5
    """
    Золотая рулетка:
    - работает по принципу русской рулетки (1 из 6 — поражение)
    - играется на монетки из фармы (таблица farma в Base_bot.db)
    - при поражении ставка сгорает
    - при выживании игрок получает +100% к ставке (удваивает поставленную сумму)
    """
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return
    # Только групповые чаты
    if message.chat.id == message.from_user.id:
        await message.answer(
            "📝Эта команда предназначена для использования в групповых чатах, а не в личных сообщениях!"
        )
        return

    if message.chat.id not in chats:
        await message.answer("кыш")
        return

    user = message.from_user
    user_id = user.id
    user_mention = GetUserByID(user_id).mention

    # Не даем играть ботам
    if getattr(user, "is_bot", False):
        await message.answer("🤖 Боты не могут играть в золотую рулетку!")
        return

    # Парсим ставку из сообщения
    # Примеры: "золотая рулетка 1000", "!золотая рулетка 500"
    bet = None
    for part in message.text.replace(",", " ").split():
        if part.isdigit():
            bet = int(part)
            break

    if bet is None:
        bet = 100  # ставка по умолчанию

    if bet <= 0:
        await message.answer("📝Ставка должна быть положительным числом.")
        return

    MIN_BET = 100
    if bet < MIN_BET:
        await message.answer(f"📝Минимальная ставка в золотой рулетке: {MIN_BET} eZ¢.")
        return

    # Работаем с мешком из таблицы farma
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()

    try:
        row = cursor.execute(
            "SELECT meshok FROM farma WHERE user_id = ?", (user_id,)
        ).fetchone()
        meshok = row[0] if row is not None else 0
    except sqlite3.Error:
        connection.close()
        await message.answer("⚠️Ошибка доступа к базе данных. Попробуй позже.")
        return

    if meshok < bet:
        await message.answer(
            f"💰 У тебя недостаточно монет для ставки.\n"
            f"В мешке сейчас: 🍊 {meshok} eZ¢\n"
            f"Твоя ставка: 🍊 {bet} eZ¢"
        )
        connection.close()
        return

    # Русская рулетка: 1 из 6 — поражение
    is_dead = random.randint(1, 6) <= 3
    
    if is_dead:
        # Проигрыш — ставка сгорает
        new_meshok = meshok - bet
        try:
            cursor.execute(
                "UPDATE farma SET meshok = ? WHERE user_id = ?", (new_meshok, user_id)
            )
            connection.commit()
        finally:
            connection.close()

        result_text = (
            f"💰 <b>Золотая рулетка</b>\n\n"
            f"{user_mention} делает ставку в размере 🍊 <b>{bet} eZ¢</b> и нажимает на спусковой крючок...\n\n"
            f"🔫 <b>БАБАХ!</b>\n\n"
            f"❌ В барабане оказался патрон. Твоя ставка сгорела.\n\n"
            f"💼 В твоем мешке осталось: 🍊 <b>{new_meshok} eZ¢</b>"
        )
        await mute_user(user_id, message.chat.id, MUTE_TIME, 'мин', message, '', bot)
    else:
        # Выигрыш — ставка удваивается (прибавляем ставку к мешку)
        win_amount = bet
        new_meshok = meshok + win_amount

        try:
            if meshok == 0:
                # если записи нет — создаем
                cursor.execute(
                    "INSERT OR IGNORE INTO farma (user_id, meshok, last_date) VALUES (?, ?, datetime('now'))",
                    (user_id, new_meshok),
                )
                cursor.execute(
                    "UPDATE farma SET meshok = ? WHERE user_id = ?",
                    (new_meshok, user_id),
                )
            else:
                cursor.execute(
                    "UPDATE farma SET meshok = ? WHERE user_id = ?",
                    (new_meshok, user_id),
                )
            connection.commit()
        finally:
            connection.close()

        result_text = (
            f"💰 <b>Золотая рулетка</b>\n\n"
            f"{user_mention} делает ставку в размере 🍊 <b>{bet} eZ¢</b> и нажимает на спусковой крючок...\n\n"
            f"✨ <i>Щелчок</i>\n\n"
            f"✅ Тебе повезло! Патронник был пуст.\n"
            f"📈 Ты выигрываешь ещё 🍊 <b>{win_amount} eZ¢</b> сверху!\n\n"
            f"💼 Теперь в твоем мешке: 🍊 <b>{new_meshok} eZ¢</b>"
        )

    await bot.send_message(
        message.chat.id,
        result_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


