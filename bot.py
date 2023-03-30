import openai, asyncio
from config import *
from aiogram import Dispatcher, Bot, executor, types
from bd_handlers import create_table_if_not_exists, add_or_check_phone, user_logged, ai_field_update, ai_exists, tryes_plus_one
from kbs import send_phone_kb, choose_ai_kb

bot = Bot(TGToken)
dp = Dispatcher(bot)

#Подключаем API
openai.api_key = GPTToken
#Все запросы всех пользователей
all_messages = {}

#Обработчик запроса к Chat Gpt
def sent_question(messages):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
    
    return completion






# Команда START
@dp.message_handler(commands=["start"])
async def start_process(msg):
    text = """REGISTRATION👾\n\nПожалуйста поделитесь номером своего телефона для регистрации👌"""
    await msg.answer(text, reply_markup=send_phone_kb())






#Обработчик телефонного номера
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def phone_handler(msg):

    phone_number = msg.contact.phone_number
    user_id = msg.from_user.id

    #Регистрируем и входим 
    await add_or_check_phone(phone_number, user_id)


    await msg.answer("Вы успешно вошли!", reply_markup=types.ReplyKeyboardRemove())
    
    #Выбор AI
    await msg.answer("Выберите AI:", reply_markup=choose_ai_kb())






# Команда CHOOSEAI
@dp.message_handler(commands=["chooseai"])
async def chooseAI_process(msg):
    #Залогинен ли пользователь
    user_id = msg.from_user.id
    user_exists = await user_logged(user_id)


    #Если пользователь залогинен, выбираем AI
    if user_exists:
        await msg.answer("Выберите AI:", reply_markup=choose_ai_kb())

    #Если не залогинен, то перенаправляем на регистрацию
    else:
        await start_process(msg)






#Команда DELETECONTEXT
@dp.message_handler(commands=["deletecontext"])
async def deletecontext_process(msg):
    global all_messages

    # ID пользователя
    user_id = msg.from_user.id
    #Залогинен ли пользователь
    user_exists = await user_logged(user_id)



    #Если пользователь зарегестрирован
    if user_exists:
        #Стираем данные
        all_messages[user_id] = []
        await msg.answer("Данные стерты😘")

    # Если нет, перенаправляем на страницу регистрации
    else:
        await start_process(msg)



    





# Обработчик callback gpt_button
@dp.callback_query_handler(text="gpt_button") #text - То, что отправили с кнопкой
async def product_location(call):
    user_id = call["from"].id
    ai_name = "ChatGPT-3.5"

    #Меняем поле ai на ChatGPT
    await ai_field_update(user_id, ai_name)

    text = """⚡️The bot uses the same model as the ChatGPT website: gpt-3.5-turbo.

Here you can perform a wide variety of natural language tasks, such as:

1. Copywriting and rewriting
2. Writing and editing code
3. Translation from any language
4. Parsing unstructured text and summarization
5. Chat

You can ask questions in any language. However, the most accurate and exciting responses seem to be in English.

Be aware: the bot may occasionally generate incorrect information and has limited knowledge of the world and events after 2021.

✉️ To get a text response, write your question into the chat.

🔄 To delete your context, send a command '/deletecontext'.

Have fun!"""

    await bot.send_message(call.message.chat.id, text=text)
    await call.answer()








#Делаем запрос к AI, когда получаем любой текст, при этом мы должны быть залогиненны.
@dp.message_handler(content_types=["text"])
async def qwestion_handler(msg):
    global all_messages

    # залогиненны ли мы:
    user_id = msg.from_user.id
    user_exists = await user_logged(user_id)

    #True если поле    ai   заполнено
    ai_exist = await ai_exists(user_id)


    #Если залогиненны
    if user_exists:
        #Если поле ai не None
        if ai_exist:


            #ChatGPT-3.5
            if ai_exist == "ChatGPT-3.5":
                reply_msg = await msg.reply("👻Обрабатываю...")
                ################################       ChatGPT Sender     ##############################################


                # Сам вопрос
                question = msg.text

                # Записываем вопрос в бд
                if all_messages.get(user_id, False):
                    all_messages[user_id].append({"role": "user", "content": question})
                else:
                    all_messages[user_id] = [{"role": "user", "content": question}]


                # Отправляем на обработку
                loop = asyncio.get_running_loop()
                completion = await loop.run_in_executor(None, sent_question, all_messages[user_id])


                # Получаем ответ
                answer = completion.choices[0].message.content

                # Добавляем ответ в память, для запоминания ответа
                all_messages[user_id].append({"role": "assistant", "content": answer})


                # К tryes + 1
                await tryes_plus_one(user_id)


                await reply_msg.delete()
                await msg.reply(answer)


                ######################################################################################################

            else:
                await msg.answer("Извиняюсь, но этот функционал еще не введен🫤")





        #Если пустое то перенаправляем
        else:
            await chooseAI_process(msg)

    # Если не залогиненны, перенаправляем на start
    else:
        await start_process(msg)














if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)