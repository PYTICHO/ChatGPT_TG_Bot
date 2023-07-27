import asyncpg
from config import *





# Если нет таблицы, создаем ее
async def create_table_if_not_exists():
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    await connection.execute('CREATE TABLE IF NOT EXISTS users(user_id VARCHAR(40) PRIMARY KEY, tryes INT, wallet INT)')
    await connection.close()



#Создание или проверка наличия НОМЕРА ТЕЛЕФОНА
async def add_or_check_user(user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    await connection.execute(f"INSERT INTO users VALUES('{user_id}', 0, 0) ON CONFLICT DO NOTHING")
    await connection.close()





#Добавление к tryes + 1
async def tryes_plus_one(user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    tryes = await connection.fetch(f"SELECT tryes FROM users WHERE user_id = '{user_id}'")

    try:
        tryes = tryes[0].get("tryes")
    except:
        pass

    #Tryes + 1
    await connection.execute(f"UPDATE users SET tryes = {tryes + 1} WHERE user_id = '{user_id}'")
    await connection.close()





#Получение поля tryes
async def get_user_tryes(user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    tryes = await connection.fetch(f"SELECT tryes FROM users WHERE user_id = '{user_id}'")
    await connection.close()

    try:
        tryes = int(tryes[0].get("tryes"))
    except:
        tryes = 0

    return tryes