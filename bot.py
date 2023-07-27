import openai, asyncio, logging, more_itertools
from config import *
from aiogram import Dispatcher, Bot, executor, types
from bd_handlers import *


#Ловим ошибки
logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w", format='%(asctime)s %(message)s')


bot = Bot(TGToken)
dp = Dispatcher(bot)

#Подключаем API
openai.api_key = GPTToken
#Все запросы всех пользователей
all_messages = {}


print(f"Бот запущен!\nTG - {TGToken}\nGPT - {GPTToken}")


#Обработчик запроса к Chat Gpt
async def sent_question(messages):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    
    return completion


#Подсчет контекста
#user_ai_context  -  [{'role': 'user', 'content': 'YOUR QUESTION'}, {'role': 'assistant', 'content': 'AI ANSWER'}]
async def get_len_of_context(user_ai_context):
    len_of_context = 0
    for block in user_ai_context:
        len_of_context += len(block["content"])

    return len_of_context






# Команда START
@dp.message_handler(commands=["start"])
async def start_process(msg):
    # ID пользователя
    user_id = msg.from_user.id

    text = """⚡️Бот использует ту же модель, что и сайт ChatGPT: gpt-3.5-turbo.

Здесь вы можете выполнять широкий спектр задач, связанных с естественным языком, таких как:

1. Копирайтинг и переписывание текстов
2. Написание и редактирование кода
3. Перевод с любого языка
4. Обработка структурированных текстов и создание сводок
5. Чат

Вы можете задавать вопросы на любом языке. Однако самые точные и увлекательные ответы обычно на английском языке.

Обратите внимание: бот может время от времени генерировать неправильную информацию и иметь ограниченные знания о мире и событиях после 2021 года.

🔄 Чтобы удалить контекст, отправьте команду «/deletecontext».

✉️ Чтобы получить текстовый ответ, напишите свой вопрос в чат.

Веселитесь!"""

    #Добавляем пользователя в бд
    await add_or_check_user(user_id=user_id)

    await msg.answer(text)



#Команда DELETECONTEXT
@dp.message_handler(commands=["deletecontext"])
async def deletecontext_process(msg):
    global all_messages

    # ID пользователя
    user_id = msg.from_user.id

    #Стираем данные
    all_messages[user_id] = []
    await msg.answer("Данные стерты😘")




#Делаем запрос к AI, когда получаем любой текст
@dp.message_handler(content_types=["text"])
async def qwestion_handler(msg):
    global all_messages

    user_id = msg.from_user.id


    #Создаем пользователя контекст
    if not all_messages.get(user_id, False):
        all_messages[user_id] = []


    reply_msg = await msg.reply("👻Обрабатываю...")
    await msg.answer_chat_action("typing")

    #Делаю 2 попытки
    for t in range(3):
        try:
            ################################       ChatGPT Sender     ##############################################
            # Сам вопрос
            question = msg.text
            dict_with_question = {"role": "user", "content": question}


            # Записываем вопрос в all_messages
            if t == 0:
                all_messages[user_id].append(dict_with_question)

            # Отправляем на обработку
            completion = await sent_question(all_messages[user_id])

            # Получаем ответ
            answer = completion.choices[0].message.content

            # Добавляем ответ в память, для запоминания ответа
            all_messages[user_id].append({"role": "assistant", "content": answer})

            if t == 0:
                # К tryes + 1
                await tryes_plus_one(user_id)

                

            #Разделяем ответ по 3300 символов, из-за вредности тг
            answer = list(more_itertools.sliced(answer, 3300))
            for ans in answer:
                await msg.reply(ans)

            #Если нет ошибок, то не делаем 2 попытку
            break
            ######################################################################################################

        #При ошибке на сервере
        except Exception as e:
            print(e.__class__.__name__)


            #Олавлимаем лимит по контексту
            if e.__class__.__name__ in ["InvalidRequestError", "RateLimitError"]:
                all_messages[user_id] = all_messages[user_id][-2:]

                #Обнуляем контекст пользователя
                if t == 2:
                    all_messages[user_id] = [dict_with_question]

                if t == 0:
                    await msg.answer("""По правилам использования ChatGPT количество символов в диалоге не может превышать лимит слов
=> Я был вынужден забыть ваш диалог, кроме последних 2 вопросов.
Но вы можете продолжать общение👌""")
                await asyncio.sleep(6)
                continue


            if t == 2:
                await msg.answer("ChatGPT перегружен, подождите немного.")
                continue

    await reply_msg.delete()



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)