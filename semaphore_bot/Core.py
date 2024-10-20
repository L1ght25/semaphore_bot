import telebot
from telebot.async_telebot import AsyncTeleBot
import random
import asyncio
import json
from collections import Counter
import os
import requests

bot = AsyncTeleBot(os.getenv('TOKEN'))
database = requests.get('http://server:8000/get-aneks', data={'password': os.getenv('PASSWORD')}).json()
anek_database = database['database_of_aneks']
best_anek = database['best_anek']
curr_finders = []
curr_dict = {}
TRESHOLD = 100

def IsBadString(string):  # фильтрация))
    return 'порн' in string.lower() or 'корейк' in string.lower() or 'карейк' in string.lower() or 'htt' in string.lower() or '.ru' in string.lower()

@bot.message_handler(commands=['start'])
async def get_start_bot(message):
    await bot.send_message(message.chat.id, "Вы пользуетесь самым лучшим ботом! Напиши /help, чтобы узнать функционал")

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
/random_replace_anek - вводишь слово, которое ты хочешь заменить и то, на которое хочешь заменить и наслаждаешься)
                       ''')

@bot.message_handler(commands=['random_anek'])
async def get_random_anek(message):
    await bot.reply_to(message, "Ух, ща такой анек скину:")
    anek_id = random.randint(1, 999)
    anek = anek_database[anek_id]
    await bot.send_message(message.chat.id, anek)

@bot.message_handler(commands=['send_semaphore'])
async def get_semaphore(message):
    sti = 'CAACAgIAAxkBAAEJU5dnFWxa3R3jHuOjMvEi0_iXhikrMAACOWUAArQ3qUjUyc7gEzJ_mDYE'
    await bot.send_sticker(message.chat.id, sti)

@bot.message_handler(commands=['best_anek'])
async def get_best_anek(message):
    await bot.send_message(message.chat.id, best_anek)

@bot.message_handler(commands=['find_anek'])
async def get_finded_anek(message):
    await bot.reply_to(message, "Набери ключевые слова:")
    curr_finders.append(message.from_user.id)


@bot.message_handler(commands=['random_replace_anek'])
async def get_replace_anek(message):
    await bot.reply_to(message, "Набери, какое слово ты хочешь заменить:")
    curr_dict[str(message.from_user.id)] = []


@bot.message_handler(commands=['random_semaphore_anek'])
async def get_short_anek(message):
    if len(anek_database) == 0:
        await bot.reply_to(message, "Шок, анеков нет!")
    while True:
        anek = random.choice(anek_database)
        if IsBadString(anek):
            continue
        split_data = anek.split()
        Counters_found = Counter(split_data)
        most_freq_word = Counters_found.most_common(1)[0][0]
        if most_freq_word == '-' or most_freq_word == '—' or len(most_freq_word) == 1:
            most_freq_word = Counters_found.most_common(2)[1][0]
        anek = anek.replace(most_freq_word, "СЕМАФОР")
        await bot.reply_to(message, "Наслаждайся")
        await bot.send_message(message.chat.id, anek)
        return

@bot.message_handler(commands=['random_short_anek'])
async def get_short_anek(message):
    answer = []
    for anek in anek_database:
        if 1 <= len(anek) <= TRESHOLD and not IsBadString(anek):
            answer.append(anek)
    if len(answer) == 0:
        await bot.reply_to(message, "Шок, коротких анеков нет!")
    anek = random.choice(answer)
    await bot.reply_to(message, anek)

async def find_anek(key, message):
    if IsBadString(key):  # антифрод))
            await bot.reply_to(message, "Ах ты маленький шалун) Не будет тебе никаких анеков! Держи семафор:")
            sti = 'CAACAgIAAxkBAAEJU5dnFWxa3R3jHuOjMvEi0_iXhikrMAACOWUAArQ3qUjUyc7gEzJ_mDYE'
            await bot.send_sticker(message.chat.id, sti)
            return -1
    answers = []
    flag = 0
    for anek in anek_database:
        if key.lower() in anek.lower() and "t.me" not in anek.lower() and not IsBadString(anek):
            if flag == 0:
                flag = 1
            answers.append(anek)
    if len(answers) == 0:
        await bot.send_message(message.chat.id, "Такого анека нет(")
        return -1
    else:
        await bot.reply_to(message, "Найдено целых {} анеков!".format(len(answers)))
        anek = random.choice(answers)
        return anek

@bot.message_handler(content_types=['text'])
async def get_key_words(message):
    key = message.text
    if message.from_user.id in curr_finders:
        curr_finders.remove(message.from_user.id)
        anek = await find_anek(key, message)
        if anek != -1:
            await bot.send_message(message.chat.id, anek)
    elif str(message.from_user.id) in curr_dict.keys() and len(curr_dict[str(message.from_user.id)]) == 0:
        key = ' ' + key
        curr_dict[str(message.from_user.id)].append(key)
        await bot.reply_to(message, "Напиши, на какое слово заменить:")
    elif str(message.from_user.id) in curr_dict.keys() and len(curr_dict[str(message.from_user.id)]) == 1:
        id_ = str(message.from_user.id)
        key = ' ' + key
        curr_dict[id_].append(key)
        anek = await find_anek(curr_dict[id_][0], message)
        if anek != -1:
            anek = anek.lower().replace(curr_dict[id_][0].lower(), curr_dict[id_][1])
            anek = anek.replace(curr_dict[id_][0].lower() + ':', curr_dict[id_][1] + ':')
            anek = anek.replace(curr_dict[id_][0].lower() + ',', curr_dict[id_][1] + ',')
            anek = anek.replace(curr_dict[id_][0].lower() + '.', curr_dict[id_][1] + '.')
            anek = anek.replace(curr_dict[id_][0].lower() + ';', curr_dict[id_][1] + ';')
            anek = anek.replace(curr_dict[id_][0].lower() + '!', curr_dict[id_][1] + '!')
            anek = anek.replace(curr_dict[id_][0].lower() + '?', curr_dict[id_][1] + '?')
            await bot.send_message(message.chat.id, anek)
        curr_dict.pop(id_, None)

if __name__ == '__main__':
    asyncio.run(bot.polling(non_stop=True))
