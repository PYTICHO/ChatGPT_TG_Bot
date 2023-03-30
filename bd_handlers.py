import asyncpg
from config import *





# Если нет таблицы, создаем ее
async def create_table_if_not_exists():
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    await connection.execute('CREATE TABLE IF NOT EXISTS users(phone VARCHAR(40) PRIMARY KEY, user_id VARCHAR(40), ai VARCHAR(40), tryes INT, subscribe INT)')
    await connection.close()



#Создание или проверка наличия НОМЕРА ТЕЛЕФОНА
async def add_or_check_phone(phone_number, user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    await connection.execute(f"INSERT INTO users VALUES('{phone_number}','{user_id}', 'None', 0, 0) ON CONFLICT DO NOTHING")
    await connection.close()



#Проверка залогинен ли пользователь или нет
async def user_logged(user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    user_exists = await connection.fetch(f"SELECT phone FROM users WHERE user_id = '{user_id}'") #Вернет True, если есть в БД id пользователя
    await connection.close()

    return bool(user_exists)



#Проверка на то заполнено ли поле ai
async def ai_exists(user_id):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    ai_exists = await connection.fetch(f"SELECT ai FROM users WHERE user_id = '{user_id}'")
    try:
        ai_exists = ai_exists[0].get("ai")
    except:
        ai_exists = "None"
    await connection.close()


    if ai_exists != "None":
        return True
    
    return False





# Изменение поля    ai    на выбранное пользователем
async def ai_field_update(user_id, ai_name):
    connection = await asyncpg.connect(user=user, password=password, database=db_name, host=host)
    await connection.execute(f"UPDATE users SET ai = '{ai_name}' WHERE user_id = '{user_id}'")
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