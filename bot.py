import openai, asyncio, logging, more_itertools
from config import *
from aiogram import Dispatcher, Bot, executor, types
from bd_handlers import *
from kbs import send_phone_kb, choose_ai_kb

#Ловим ошибки
logging.basicConfig(level=logging.INFO)


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
    text = """REGISTRATION👾\n\nПожалуйста поделитесь номером своего телефона для регистрации👌"""
    await msg.answer(text, reply_markup=send_phone_kb())






#Обработчик телефонного номера
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def phone_handler(msg):

    user_id = msg.from_user.id

    phone_number = msg.contact.phone_number
    #Если номер телефона начинается с +, то убираем +
    if str(phone_number).startswith("+"):
        phone_number = phone_number[1:]



    #Регистрируем и входим 
    await add_or_check_phone(phone_number, user_id)

    await msg.answer("🎆Вы успешно вошли!🎆", reply_markup=types.ReplyKeyboardRemove())
    
    #Выбор AI
    await msg.answer("Выберите AI🤖:", reply_markup=choose_ai_kb())






# Команда CHOOSEAI
@dp.message_handler(commands=["chooseai"])
async def chooseAI_process(msg):
    #Залогинен ли пользователь
    user_id = msg.from_user.id
    user_exists = await user_logged(user_id)


    #Если пользователь залогинен, выбираем AI
    if user_exists:
        await msg.answer("Выберите AI🤖:", reply_markup=choose_ai_kb())

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
        all_messages[user_id] = {}
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

    #Кол-во попыток(tryes) пользователя 
    # tryes = await get_user_tryes(user_id)   -     Пока не нужно


    #Если залогиненны
    if user_exists:
        #Если поле ai не None
        if ai_exist:

            reply_msg = await msg.reply("👻Обрабатываю...")
            #Делаю 2 попытки
            for t in range(2):
                try:
                    #ChatGPT-3.5
                    if ai_exist == "ChatGPT-3.5":

                        ################################       ChatGPT Sender     ##############################################
                        # Сам вопрос
                        question = msg.text
                        dict_with_question = {"role": "user", "content": question}


                        # Записываем вопрос в all_messages
                        if t == 0:
                            if all_messages.get(user_id, False):
                                #Длина контекста
                                len_of_context = await get_len_of_context(all_messages[user_id][ai_exist]) + len(question)


                                #Если контекста не больше лимита символов, то добавляем в all_messages
                                if len_of_context <= 5000:
                                    all_messages[user_id][ai_exist].append(dict_with_question)
                                
                                #Если контекст превышает лимит, то обнуляем контекст
                                else:
                                    await msg.answer("""🫤По правилам использования ChatGPT количество символов в диалоге не может превышать 4000
        => Я был вынужден забыть ваш диалог...
        Можете продолжать общение👌""")
                                    
                                    all_messages[user_id] = {ai_exist: [dict_with_question]}


                            #если нет в бд, то создаем для пользователя список вопросов
                            else:
                                all_messages[user_id] = {ai_exist: [dict_with_question]}
                            


                        # Отправляем на обработку
                        loop = asyncio.get_running_loop()
                        completion = await loop.run_in_executor(None, sent_question, all_messages[user_id][ai_exist])


                        # Получаем ответ
                        answer = completion.choices[0].message.content

                        # Добавляем ответ в память, для запоминания ответа
                        all_messages[user_id][ai_exist].append({"role": "assistant", "content": answer})

                        # К tryes + 1
                        await tryes_plus_one(user_id)

                            

                        #Разделяем ответ по 3300 символов, из-за вредности тг
                        answer = list(more_itertools.sliced(answer, 3300))
                        for ans in answer:
                            await msg.reply(ans)

                        #Если нет ошибок, то не делаем 2 попытку
                        break
                        ######################################################################################################

                    #elif ai_exist =="....":

                    else:
                        await msg.answer("Извиняюсь, но этот функционал еще не введен🫤")

                #При ошибке на сервере
                except Exception as e:
                    if t == 1:
                        await msg.answer("Ошибка на сервере🫤, либо попробуйте заново👌")
                    print(e)
                    continue

            await reply_msg.delete()

        #Если поле ai пустое, то перенаправляем на выбор AI
        else:
            await chooseAI_process(msg)

    # Если не залогиненны, перенаправляем на start
    else:
        await start_process(msg)





if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)