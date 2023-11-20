import telebot
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()


myclient = pymongo.MongoClient(os.getenv('MONGODB_SECRET'))
mydb = myclient["Cluster0"]
mycol = mydb["feedbacks"]
myusers = mydb["auth"]
feedbackUsers = []
signUsers = []
passwordUsers = []
passwordMap = {}
bot = telebot.TeleBot(os.getenv('BOT_SECRET'))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Қош келдіңіз!" + "\n" + "/description - Қысқаша түсініктеме" + "\n" + "/getfeeds + Пікірлерді көру" + "\n" + "/feedback + Пікір қалдыру")


@bot.message_handler(commands=['description'])
def send_description(message):
    bot.reply_to(message,
                 "Бұл бот арқылы сіз:\nКері байланыс жасау\nБағалау\nҮй тапсрымасын жіберу\nсекілді әрекеттер жасай аласыз")


@bot.message_handler(commands=['getfeeds'])
def send_givefeedbacks(message):
    mes = '';
    for res in mycol.find():
        username = res['message']['from']['username']
        name = res['message']['from']['first_name']
        text = res['message']['text']
        mes += "Қолданушы: @" + username + "\n" + "Есімі: " + name + "\n" + text + "\n"
    bot.reply_to(message, mes)


@bot.message_handler(commands=['feedback'])
def send_feedback(message):
    feedbackUsers.append(message.from_user.id)
    bot.reply_to(message, 'Өз пікіріңізді жазыңыз')

@bot.message_handler(commands=['signin'])
def send_login(message):
    signUsers.append(message.from_user.id)
    bot.reply_to(message, 'Төменге логин жазыңыз')


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.from_user.id in feedbackUsers:
        feedbackUsers.remove(message.from_user.id)
        mycol.insert_one({"message": {"from": {"username": message.from_user.username, "first_name": message.from_user.first_name}, "text": message.text}})
        bot.reply_to(message, 'Пікіріңізге рахмет!')
    if (message.from_user.id) in signUsers:
        signUsers.remove(message.from_user.id)
        passwordUsers.append(message.from_user.id)
        passwordMap[message.from_user.id] = message.text
        bot.reply_to(message, 'Төменге пароль жазыңыз')
    elif (message.from_user.id) in passwordUsers:
        passwordUsers.remove(message.from_user.id)
        temp = myusers.find_one({"info": {"login": passwordMap[message.from_user.id], "password": message.text}})
        del passwordMap[message.from_user.id]
        if temp is not None:
            bot.reply_to(message, 'Қош келдіңіз')
        else:
            bot.reply_to(message, 'Деректер табылмады')


bot.infinity_polling()