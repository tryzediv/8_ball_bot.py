import random
import telebot
from telebot import types
from time import sleep

bot = telebot.TeleBot('TOKEN')
# Ответы для шара восьмерки
answers = ['Бесспорно', 'Предрешено', 'Никаких сомнений', 'Определённо да',
           'Можешь быть уверен в этом', 'Мне кажется — «да»', 'Вероятнее всего',
           'Хорошие перспективы', 'Знаки говорят — «да»', 'Да', 'Пока не ясно, попробуй снова',
           'Спроси позже', 'Лучше не рассказывать', 'Сейчас нельзя предсказать',
           'Сконцентрируйся и спроси опять', 'Даже не думай', 'Мой ответ — «нет»',
           'По моим данным — «нет»', 'Перспективы не очень хорошие', 'Весьма сомнительно']
# Имена и ответы для гадания по имени
names = []
variables = ['Враги', 'Друзья', 'Любовь', 'Общение']
# Обойма для револьвера
clip = []
spin = 0


# Стартовое сообщение бота
@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(message.chat.id, "Задай вопрос шару, на который можно ответить Да или Нет")


# Режим гадания по имени
@bot.message_handler(commands=['name'])
def name(message):
    bot.send_message(message.chat.id, "Напиши первое имя")
    bot.register_next_step_handler(message, step_1)


def step_1(message):
    name_1 = message.text
    names.append(name_1)
    bot.send_message(message.chat.id, "Напиши второе имя")
    bot.register_next_step_handler(message, step_2)


def step_2(message):
    name_2 = message.text
    names.append(name_2)
    answer = variables[(len(names[0]) + len(names[1])) % len(variables)]
    bot.send_message(message.chat.id, '{} + {} = {}'.format(names[0], names[1], answer))
    names.clear()


# Игра русская рулетка
@bot.message_handler(commands=['roulette'])
def start_game(message):
    global spin
    clip.clear()
    spin = 0
    bot.send_message(message.chat.id, 'Сколько патронов зарядить? Напиши от 1 до 6')
    bot.register_next_step_handler(message, roulette_1)


def roulette_1(message):
    bullets = message.text
    keyboard = types.InlineKeyboardMarkup()
    key_roll = types.InlineKeyboardButton(text='Крутануть барабан', callback_data='roll')
    keyboard.add(key_roll)
    key_shot = types.InlineKeyboardButton(text='Спустить курок', callback_data='shot')
    keyboard.add(key_shot)
    if bullets.isdigit():
        if int(bullets) >= 6:
            sleep(.5)
            bot.reply_to(message, text='Револьвер заряжен полностью, удачи!',
                         reply_markup=keyboard)
            for i in range(6):
                clip.append(1)
        else:
            for i in range(6):
                clip.append(int(bullets))
                bullets = int(bullets) - 1
            sleep(.5)
            bot.reply_to(message,
                         text='Револьвер заряжен',
                         reply_markup=keyboard)
        random.shuffle(clip)
    else:
        start_game(message=bot.reply_to(message, 'Нужно ввести число'))


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    keyboard = types.InlineKeyboardMarkup()
    key_roll = types.InlineKeyboardButton(text='Крутануть барабан', callback_data='roll')
    keyboard.add(key_roll)
    key_shot = types.InlineKeyboardButton(text='Спустить курок', callback_data='shot')
    keyboard.add(key_shot)
    global spin
    if call.data == 'shot':
        try:
            if clip[spin] > 0:
                bot.send_message(call.message.chat.id, 'Бабах!')
                spin += 1
            elif clip[spin] <= 0:
                spin += 1
                bot.send_message(call.message.chat.id, '*Щелк*', reply_markup=keyboard)
        except IndexError:
            bot.send_message(call.message.chat.id, 'Барабан пуст')
    if call.data == "roll":
        spin = 0
        random.shuffle(clip)
        bot.send_message(call.message.chat.id, '*Звук вращающегося барабана*', reply_markup=keyboard)


# Ответ на сообщение, рандом из списка ответов
@bot.message_handler(content_types=['text'])
def echo(message):
    random.shuffle(answers)
    sleep(.5)
    bot.send_message(message.chat.id, random.choice(answers))


# Режим вызова бота в чатах
@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    random.shuffle(answers)
    message = random.choice(answers)
    random.shuffle(answers)
    r = types.InlineQueryResultArticle(
        id='1', title="Волшебный шар даст ответ",
        description='Нажми, чтобы узнать',
        input_message_content=types.InputTextMessageContent(message_text='{}\n{}'.format(query.query, message)))
    bot.answer_inline_query(query.id, [r])


bot.polling(none_stop=True)
