import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main.secret import admin_token as token
from aiogram import Router, Bot, Dispatcher, types, F
from path import Path
import datetime
import aiogram
from aiogram.filters import Command
import password_generator
import main.secret

#? EN: User IDs allowed to create new links
#* RU: ID пользователей, которым разрешено создавать новые ссылки
can_new_link_users = [8015726709, 1401086794, 1240656726]
#? EN: User IDs allowed to create recommendations
#* RU: ID пользователей, которым разрешено создавать рекомендации
can_recommend_users = [8015726709, 1401086794, 1240656726, 5714854312, 1803851598]
#? EN: User IDs allowed to access admin panel
#* RU: ID пользователей, которым разрешен доступ к админ-панели
can_admin_panel = [8015726709, 1401086794, 1240656726]

#? EN: Database paths configuration
#* RU: Конфигурация путей к базам данных
curent_path = (Path(__file__)).parent.parent
main_path = curent_path / 'databases' / 'Base_bot.db'
warn_path = curent_path / 'databases' / 'warn_list.db'
datahelp_path = curent_path / 'databases' / 'my_database.db'
tur_path = curent_path / 'databases' / 'tournaments.db'
dinamik_path = curent_path / 'databases' / 'din_data.db'



#? EN: Import working chat IDs from database
#* RU: Импорт ID рабочих чатов из базы данных
connection = sqlite3.connect(main_path, check_same_thread=False)
cursor = connection.cursor()
logs_gr = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('logs_gr',)).fetchall()[0][0])
sost_1 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_1',)).fetchall()[0][0])
sost_2 = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('sost_2',)).fetchall()[0][0])
klan = -int(cursor.execute(f"SELECT chat_id FROM chat_ids WHERE chat_name = ?", ('klan',)).fetchall()[0][0])

TOKEN = main.secret.admin_token
bot = Bot(token=TOKEN)
router = Router(name=__name__)