import telebot
from telebot.async_telebot import AsyncTeleBot
import random
import asyncio
import json
import key
from collections import Counter


bot = AsyncTeleBot(key.TOKEN)
database = json.load(open('database.json'))
anek_database = database['database_of_aneks']
best_anek = database['best_anek']
TRESHOLD = 100

def IsBadString(string):  # антифрод))
    return 'порн' in string.lower() or 'корейк' in string.lower() or 'карейк' in string.lower()

@bot.message_handler(commands=['start'])
async def get_start_bot(message):
    await bot.send_message(message.from_user.id, "Вы пользуетесь самым лучшим ботом! Напиши /help, чтобы узнать функционал")

@bot.message_handler(commands=['help'])
async def get_text_messages(message):
    await bot.reply_to(message,
                       '''
                       Список моих команд:
/help - если что-то непонятно(
/random_anek - скидывает рандомный анекдот из огромной базы данных
/send_semaphore - ну вы поняли)
/best_anek - самый лучший анек на свете
/find_anek - ищет в базе данных анек с заданными ключевыми словами
/random_short_anek - скидывает рандомный короткий анекдот (до 100 символов)
/random_semaphore_anek - killer feature, заменяет самое частое слово на СЕМАФОР
                       ''')

@bot.message_handler(commands=['random_anek'])
async def get_random_anek(message):
    await bot.reply_to(message, "Ух, ща такой анек скину:")
    anek_id = random.randint(1, 999)
    anek = anek_database[anek_id]
    await bot.send_message(message.chat.id, anek)
    
@bot.message_handler(commands=['send_semaphore'])
async def get_semaphore(message):
    sti = 'CAACAgIAAxkBAAEGz15jmGIDy_QFu7QoXvX4UP4k7Fz6xAACwhcAAmsgUEjKrGkqZXjZESwE'
    await bot.send_sticker(message.chat.id, sti)

@bot.message_handler(commands=['best_anek'])
async def get_best_anek(message):
    await bot.send_message(message.chat.id, best_anek)

@bot.message_handler(commands=['find_anek'])
async def get_finded_anek(message):
    await bot.send_message(message.chat.id, "Набери ключевые слова:")
    curr_finders = json.load(open('curr_finders.json'))
    curr_finders.append(message.from_user.id)
    with open('curr_finders.json', 'w') as outfile:
        json.dump(curr_finders, outfile)

@bot.message_handler(commands=['random_semaphore_anek'])
async def get_short_anek(message):
    if len(anek_database) == 0:
        bot.reply_to(message, "Шок, анеков нет!")
    while True:
        anek = random.choice(anek_database)
        if IsBadString(anek):
            continue
        split_data = anek.split()
        Counters_found = Counter(split_data)
        most_freq_word = Counters_found.most_common(1)[0][0]
        if most_freq_word == '-' or most_freq_word == '—' or most_freq_word == '--':
            most_freq_word = Counters_found.most_common(2)[1][0]
        anek = anek.replace(most_freq_word, "СЕМАФОР")
        await bot.reply_to(message, "Наслаждайся")
        await bot.send_message(message.chat.id, anek)
        return

@bot.message_handler(commands=['random_short_anek'])
async def get_short_anek(message):
    answer = []
    for anek in anek_database:
        if len(anek) <= TRESHOLD and not IsBadString(anek):
            answer.append(anek)
    if len(answer) == 0:
        bot.reply_to(message, "Шок, коротких анеков нет!")
    anek = random.choice(answer)
    await bot.reply_to(message, anek)

@bot.message_handler(content_types=['text'])
async def get_key_words(message):
    key = message.text
    if IsBadString(key):  # антифрод))
        await bot.reply_to(message, "Ах ты маленький шалун) Не будет тебе никаких анеков! Держи семафор:")
        sti = 'CAACAgIAAxkBAAEGz15jmGIDy_QFu7QoXvX4UP4k7Fz6xAACwhcAAmsgUEjKrGkqZXjZESwE'
        await bot.send_sticker(message.chat.id, sti)
        return
    curr_finders = json.load(open('curr_finders.json'))
    if message.from_user.id in curr_finders:
        curr_finders.remove(message.from_user.id)
        with open('curr_finders.json', 'w') as outfile:
            json.dump(curr_finders, outfile)
        answers = []
        flag = 0
        for anek in anek_database:
            if key.lower() in anek.lower() and "t.me" not in anek.lower() and not IsBadString(anek):
                if flag == 0:
                    await bot.reply_to(message, "O, такой анек нашёлся!")
                    flag = 1
                answers.append(anek)
        if len(answers) == 0:
            await bot.send_message(message.chat.id, "Такого анека нет(")
        else:
            anek = random.choice(answers)
            await bot.send_message(message.chat.id, anek)


asyncio.run(bot.polling(non_stop=True))
