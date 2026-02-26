from main.config3 import *

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

print(get_recom(5740021109))