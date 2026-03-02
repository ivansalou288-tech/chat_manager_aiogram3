from admin_config import *
import asyncio
import json

print('start')
#? EN: Handles /start command and shows admin bot main menu with available actions.
#* RU: Обрабатывает команду /start и показывает главное меню админ-бота с доступными действиями.
@router.message(Command(commands="start"))
async def start(message: types.Message):
    print(message.from_user.id)
    buttons = [
        types.InlineKeyboardButton(text="Создать новую ссылку", callback_data="new_chat_link_check"),
        types.InlineKeyboardButton(text="Создать рекомендацию", callback_data="recommend_check"),
        types.InlineKeyboardButton(text="Снять рекомендацию", callback_data="recommend_check_snat"),
        types.InlineKeyboardButton(text="Админ - панель", callback_data="admn_panell_check"),
        
        types.InlineKeyboardButton(text="📚 Документация", url='https://ivansalou288-tech.github.io/chat_manager_bot/html/admin_guide.html'),

    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button] for button in buttons])

    await message.answer("Приветствуем в админ боте\n\nЧто хочешь сделать?", reply_markup=keyboard)

@router.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    print('web_app_data_handler', getattr(message, 'content_type', None), getattr(getattr(message, 'web_app_data', None), 'data', None))
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Не удалось прочитать данные из MiniApp")
        return

    if isinstance(data, dict) and data.get('type') == 'created_link':
        link = data.get('link')
        if link:
            await message.answer(f"Ссылка: <code>{link}</code>", parse_mode='HTML')
            return

    await message.answer("Получены данные из MiniApp")

@router.message(F.content_type == 'web_app_data')
async def web_app_data_handler_ct(message: types.Message):
    print('web_app_data_handler_ct', getattr(message, 'content_type', None), getattr(getattr(message, 'web_app_data', None), 'data', None))
    try:
        raw = message.web_app_data.data
        data = json.loads(raw) if raw else None
    except Exception:
        await message.answer("Не удалось прочитать данные из MiniApp")
        return

    if isinstance(data, dict) and data.get('type') == 'created_link':
        link = data.get('link')
        if link:
            await message.answer(f"Ссылка: <code>{link}</code>", parse_mode='HTML')
            return

    await message.answer("Получены данные из MiniApp")
print('start2')
from new_link import *
from admin.recommend import *
from admin.admin_panel import *


async def main() -> None:
    try:
        bot = Bot(token=TOKEN)
        dp = Dispatcher()
    
        dp.include_router(router)
    
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)
        await main()
if __name__ == "__main__":

    asyncio.run(main())