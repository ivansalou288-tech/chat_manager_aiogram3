import asyncio
import time
import html
import secrets
from dataclasses import dataclass
from typing import Optional
import sys
import os
import sqlite3
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from main.config3 import main_path, GetUserByMessage

router = Router()


#? token="8451829699:AAE_tfApKWq3r82i0U7yD98RCcQPIMmMT1Q"
#? api_id =21842840
#? api_hash ="1db0b6e807c90e6364287ad8af7fa655"
#? bot = Bot(token=token)
#? dp = Dispatcher(bot)

#? EN: Duel expiration time in seconds
#* RU: Время истечения дуэли в секундах
DUEL_EXPIRES_SECONDS = 90

#? EN: Data class representing a cubes duel between two players
#* RU: Класс данных, представляющий дуэль на кубиках между двумя игроками
@dataclass
class _CubesDuel:
    duel_id: str
    chat_id: int
    inviter_id: int
    opponent_id: int
    inviter_name: str
    opponent_name: str
    invite_message_id: int
    created_at: float
    stake: int

#? EN: Storage for pending duels
#* RU: Хранилище ожидающих дуэлей
_PENDING_BY_CHAT: dict[int, str] = {}   #? chat_id -> duel_id
_PENDING_BY_ID: dict[str, _CubesDuel] = {}  #? duel_id -> duel


#? EN: Creates HTML link to user
#* RU: Создаёт HTML-ссылку на пользователя
def _user_link(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{html.escape(name)}</a>'

#? EN: Checks if duel has expired
#* RU: Проверяет, истекла ли дуэль
def _is_expired(duel: _CubesDuel) -> bool:
    return (time.monotonic() - duel.created_at) > DUEL_EXPIRES_SECONDS

#? EN: Parses stake amount from command text
#* RU: Извлекает размер ставки из текста команды
def _parse_stake(text: str) -> Optional[int]:
    """
    Поддерживает:
      - "!кубы 100"
      - "! кубы 100"
      - без ставки -> 100
    """
    if not text:
        return 100
    raw = text.strip()
    low = raw.lower()
    tail = ""
    if low.startswith("!кубы"):
        tail = raw[len("!кубы"):].strip()
    elif low.startswith("! кубы"):
        tail = raw[len("! кубы"):].strip()
    else:
        return None

    if not tail:
        return 100

    token = tail.split()[0]
    try:
        return int(token)
    except Exception:
        return None


#? EN: Ensures user has a row in farma table and returns their meshok balance
#* RU: Обеспечивает наличие записи пользователя в таблице farma и возвращает баланс мешка
def _ensure_farma_row_and_get_meshok(cursor: sqlite3.Cursor, user_id: int) -> int:
    row = cursor.execute("SELECT meshok FROM farma WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        cursor.execute(
            "INSERT INTO farma (user_id, meshok, last_date) VALUES (?, ?, ?)",
            (user_id, 0, datetime.now().strftime("%H:%M:%S %d.%m.%Y")),
        )
        return 0
    try:
        return int(row[0] or 0)
    except Exception:
        return 0


#? EN: Gets user's meshok balance from database
#* RU: Получает баланс мешка пользователя из базы данных
def _get_meshok(user_id: int) -> int:
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        meshok = _ensure_farma_row_and_get_meshok(cursor, int(user_id))
        connection.commit()
        return int(meshok)
    finally:
        try:
            connection.close()
        except Exception:
            pass


#? EN: Expires a duel after timeout and updates the message
#* RU: Завершает дуэль по истечении времени и обновляет сообщение
async def _expire_duel_later(duel_id: str, bot: Bot):
    await asyncio.sleep(DUEL_EXPIRES_SECONDS)
    duel = _PENDING_BY_ID.get(duel_id)
    if duel is None:
        return
    if not _is_expired(duel):
        return

    _PENDING_BY_ID.pop(duel_id, None)
    if _PENDING_BY_CHAT.get(duel.chat_id) == duel_id:
        _PENDING_BY_CHAT.pop(duel.chat_id, None)

    try:
        await bot.edit_message_text(
            chat_id=duel.chat_id,
            message_id=duel.invite_message_id,
            text=(
                "⏳ Дуэль на кубиках истекла.\n\n"
                f"{_user_link(duel.inviter_id, duel.inviter_name)} vs {_user_link(duel.opponent_id, duel.opponent_name)}"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except (TelegramBadRequest, Exception):
        # Message could be deleted/edited; ignore.
        pass


#? EN: Extracts opponent ID from message (reply or mention)
#* RU: Извлекает ID противника из сообщения (ответ или упоминание)
def _extract_opponent_id(message: Message) -> Optional[int]:
    if message.reply_to_message and message.reply_to_message.from_user:
        return int(message.reply_to_message.from_user.id)
    try:
        uid = GetUserByMessage(message).user_id
        if uid:
            return int(uid)
    except Exception:
        pass
    return None


#? EN: Handles the "!кубы" command – creates a duel invite between two users with a configurable stake in eZ¢.
#* RU: Обрабатывает команду «!кубы» – создаёт приглашение в дуэль на кубиках между двумя пользователями с настраиваемой ставкой в eZ¢.
@router.message(F.text.lower().startswith(("! кубы", "!кубы")))
async def cubes_duel_invite(message: Message, bot: Bot):
    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    black_list=[]
    blk = cursor.execute('SELECT user_id FROM black_list').fetchall()
    for i in blk:
        black_list.append(i[0])

    if message.from_user.id in black_list:
        await message.answer('В доступе отказано, ты в черном списке')
        return
    chat_id = message.chat.id
    inviter_id = message.from_user.id

    opponent_id = _extract_opponent_id(message)
    if not opponent_id:
        await message.reply(
            "🎲 Чтобы вызвать на дуэль, ответь на сообщение игрока командой:\n"
            "<b>! кубы 100</b>",
            parse_mode="HTML",
        )
        return

    if opponent_id == inviter_id:
        await message.reply("Нельзя вызвать на дуэль самого себя 🙂")
        return

    stake = _parse_stake(message.text or "")
    if stake is None:
        await message.reply("🎲 Формат: <b>! кубы 100</b> (ставка — целое число)", parse_mode="HTML")
        return
    if stake < 1:
        await message.reply("🎲 Ставка должна быть больше 0.")
        return

    inviter_meshok = _get_meshok(inviter_id)
    if inviter_meshok < stake:
        await message.reply(
            f"💰 У тебя недостаточно монет для ставки.\n"
            f"Твой мешок: 🍊 {inviter_meshok} eZ¢\n"
            f"Ставка: 🍊 {stake} eZ¢",
            parse_mode="HTML",
        )
        return

    # Only one pending duel per chat (simple and predictable).
    existing_id = _PENDING_BY_CHAT.get(chat_id)
    if existing_id:
        existing = _PENDING_BY_ID.get(existing_id)
        if existing and not _is_expired(existing):
            await message.reply(
                "⏳ В этом чате уже есть активный вызов на кубики. Дождитесь ответа или истечения таймера."
            )
            return
        # Cleanup stale
        _PENDING_BY_CHAT.pop(chat_id, None)
        if existing:
            _PENDING_BY_ID.pop(existing.duel_id, None)

    duel_id = secrets.token_hex(4)
    inviter_name = message.from_user.full_name or "Игрок 1"
    opponent_name = (
        message.reply_to_message.from_user.full_name
        if message.reply_to_message and message.reply_to_message.from_user
        else "Игрок 2"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"cubes_accept:{duel_id}"),
            InlineKeyboardButton(text="❌ Отказаться", callback_data=f"cubes_decline:{duel_id}"),
        ]
    ])

    invite_text = (
        "🎲 <b>Дуэль на кубиках!</b>\n\n"
        f"{_user_link(inviter_id, inviter_name)} вызывает {_user_link(opponent_id, opponent_name)}.\n\n"
        f"💸 Ставка: 🍊 <b>{stake}</b> eZ¢\n\n"
        f"У {html.escape(opponent_name)} есть {DUEL_EXPIRES_SECONDS} сек, чтобы принять вызов."
    )

    sent = await message.answer(invite_text, parse_mode="HTML", reply_markup=keyboard, disable_web_page_preview=True)

    duel = _CubesDuel(
        duel_id=duel_id,
        chat_id=chat_id,
        inviter_id=inviter_id,
        opponent_id=opponent_id,
        inviter_name=inviter_name,
        opponent_name=opponent_name,
        invite_message_id=sent.message_id,
        created_at=time.monotonic(),
        stake=int(stake),
    )
    _PENDING_BY_CHAT[chat_id] = duel_id
    _PENDING_BY_ID[duel_id] = duel

    asyncio.create_task(_expire_duel_later(duel_id, bot))


#? EN: Accepts a cubes duel, checks both players’ balances, rolls dice and transfers the stake to the winner.
#* RU: Принимает дуэль на кубиках, проверяет балансы обоих игроков, бросает кубики и переводит ставку победителю.
@router.callback_query(lambda c: c.data and c.data.startswith("cubes_accept:"))
async def cubes_duel_accept(call: CallbackQuery, bot: Bot):
    duel_id = call.data.split(":", 1)[1]
    duel = _PENDING_BY_ID.get(duel_id)
    if duel is None:
        await bot.answer_callback_query(call.id, text="Этот вызов уже недоступен.")
        return

    if call.message.chat.id != duel.chat_id:
        await bot.answer_callback_query(call.id, text="Этот вызов не из этого чата.")
        return

    if _is_expired(duel):
        _PENDING_BY_ID.pop(duel_id, None)
        if _PENDING_BY_CHAT.get(duel.chat_id) == duel_id:
            _PENDING_BY_CHAT.pop(duel.chat_id, None)
        await bot.answer_callback_query(call.id, text="Вызов истёк.")
        return

    # Only opponent can accept.
    if call.from_user.id != duel.opponent_id:
        await bot.answer_callback_query(call.id, text="Не для тебя кнопка 🙂")
        return

    # Remove duel immediately to prevent double-accept race.
    _PENDING_BY_ID.pop(duel_id, None)
    if _PENDING_BY_CHAT.get(duel.chat_id) == duel_id:
        _PENDING_BY_CHAT.pop(duel.chat_id, None)

    # Проверяем, что у обоих есть деньги на ставку (если нет — отменяем).
    stake = int(getattr(duel, "stake", 0) or 0)
    if stake < 1:
        stake = 100

    connection = sqlite3.connect(main_path, check_same_thread=False)
    cursor = connection.cursor()
    try:
        inviter_meshok = _ensure_farma_row_and_get_meshok(cursor, duel.inviter_id)
        opponent_meshok = _ensure_farma_row_and_get_meshok(cursor, duel.opponent_id)
        connection.commit()
    finally:
        try:
            connection.close()
        except Exception:
            pass

    if inviter_meshok < stake or opponent_meshok < stake:
        try:
            await call.message.edit_text(
                "❌ Дуэль отменена: у одного из игроков недостаточно монет для ставки.\n\n"
                f"💸 Ставка: 🍊 <b>{stake}</b> eZ¢\n"
                f"{_user_link(duel.inviter_id, duel.inviter_name)} — 🍊 <b>{inviter_meshok}</b> eZ¢\n"
                f"{_user_link(duel.opponent_id, duel.opponent_name)} — 🍊 <b>{opponent_meshok}</b> eZ¢",
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
        except (TelegramBadRequest, Exception):
            pass
        await bot.answer_callback_query(call.id, text="")
        return

    try:
        await call.message.edit_text(
            "✅ Вызов принят!\n\n"
            f"{_user_link(duel.inviter_id, duel.inviter_name)} vs {_user_link(duel.opponent_id, duel.opponent_name)}\n"
            f"💸 Ставка: 🍊 <b>{stake}</b> eZ¢\n"
            "Бросаем кубики…",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except (TelegramBadRequest, Exception):
        pass

    await bot.answer_callback_query(call.id, text="")

    # Roll two TG dice (🎲): first inviter, then opponent.
    m1 = await bot.send_dice(duel.chat_id, emoji="🎲")
    m2 = await bot.send_dice(duel.chat_id, emoji="🎲")
    await asyncio.sleep(3)
    try:
        v1 = int(getattr(m1.dice, "value", 0))
    except Exception:
        v1 = int(m1["dice"]["value"])
    try:
        v2 = int(getattr(m2.dice, "value", 0))
    except Exception:
        v2 = int(m2["dice"]["value"])

    if v1 > v2:
        winner_id, winner_name = duel.inviter_id, duel.inviter_name
        loser_id, loser_name = duel.opponent_id, duel.opponent_name
        result = f"🏆 Победил(а): {_user_link(winner_id, winner_name)}"
    elif v2 > v1:
        winner_id, winner_name = duel.opponent_id, duel.opponent_name
        loser_id, loser_name = duel.inviter_id, duel.inviter_name
        result = f"🏆 Победил(а): {_user_link(winner_id, winner_name)}"
    else:
        winner_id = None
        loser_id = None
        result = "🤝 Ничья!"

    # Перевод ставки проигравшего победителю + показываем мешки обоих.
    if winner_id is not None and loser_id is not None:
        connection = sqlite3.connect(main_path, check_same_thread=False)
        cursor = connection.cursor()
        try:
            winner_meshok = _ensure_farma_row_and_get_meshok(cursor, int(winner_id))
            loser_meshok = _ensure_farma_row_and_get_meshok(cursor, int(loser_id))

            # Если внезапно денег стало меньше (между принятием и броском) — отменяем перевод.
            if loser_meshok >= stake:
                cursor.execute("UPDATE farma SET meshok = meshok - ? WHERE user_id = ?", (stake, int(loser_id)))
                cursor.execute("UPDATE farma SET meshok = meshok + ? WHERE user_id = ?", (stake, int(winner_id)))
                connection.commit()
                winner_meshok = winner_meshok + stake
                loser_meshok = loser_meshok - stake
            else:
                connection.commit()

        finally:
            try:
                connection.close()
            except Exception:
                pass

        bags_text = (
            f"\n\n💸 Ставка: 🍊 <b>{stake}</b> eZ¢\n"
            f"✅ {_user_link(winner_id, winner_name)} забрал(а) ставку {_user_link(loser_id, loser_name)}\n\n"
            f"💰 Мешок победителя: 🍊 <b>{winner_meshok}</b> eZ¢\n"
            f"💰 Мешок проигравшего: 🍊 <b>{loser_meshok}</b> eZ¢"
        )
    else:
        inviter_meshok = _get_meshok(duel.inviter_id)
        opponent_meshok = _get_meshok(duel.opponent_id)
        bags_text = (
            f"\n\n💸 Ставка: 🍊 <b>{stake}</b> eZ¢\n"
            f"💰 Мешок {_user_link(duel.inviter_id, duel.inviter_name)}: 🍊 <b>{inviter_meshok}</b> eZ¢\n"
            f"💰 Мешок {_user_link(duel.opponent_id, duel.opponent_name)}: 🍊 <b>{opponent_meshok}</b> eZ¢"
        )

    await bot.send_message(
        duel.chat_id,
        (
            "🎲 <b>Результат дуэли</b>\n\n"
            f"{_user_link(duel.inviter_id, duel.inviter_name)}: <b>{v1}</b>\n"
            f"{_user_link(duel.opponent_id, duel.opponent_name)}: <b>{v2}</b>\n\n"
            f"{result}"
            f"{bags_text}"
        ),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


#? EN: Declines a cubes duel invite and cancels it for the chat.
#* RU: Отклоняет приглашение на дуэль в кубики и отменяет его для чата.
@router.callback_query(lambda c: c.data and c.data.startswith("cubes_decline:"))
async def cubes_duel_decline(call: CallbackQuery, bot: Bot):
    duel_id = call.data.split(":", 1)[1]
    duel = _PENDING_BY_ID.get(duel_id)
    if duel is None:
        await bot.answer_callback_query(call.id, text="Этот вызов уже недоступен.")
        return

    # Allow only inviter or opponent to decline.
    if call.from_user.id not in (duel.inviter_id, duel.opponent_id):
        await bot.answer_callback_query(call.id, text="Не для тебя кнопка 🙂")
        return

    _PENDING_BY_ID.pop(duel_id, None)
    if _PENDING_BY_CHAT.get(duel.chat_id) == duel_id:
        _PENDING_BY_CHAT.pop(duel.chat_id, None)

    try:
        await call.message.edit_text(
            "❌ Дуэль отменена.\n\n"
            f"{_user_link(duel.inviter_id, duel.inviter_name)} vs {_user_link(duel.opponent_id, duel.opponent_name)}",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    except (TelegramBadRequest, Exception):
        pass

    await bot.answer_callback_query(call.id, text="Ок")


