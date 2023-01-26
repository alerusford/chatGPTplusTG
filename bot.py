import openai
import config
import telebot
import requests
from telebot import types
import json
import traceback
import time

openai.api_key = config.openai_apikey
bot = telebot.TeleBot(config.telegram_apikey)

bot.send_message('1077463086', 'i`m online 🫡')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот, который поможет тебе использовать OpenAI API для генерации текста.')

@bot.message_handler(func=lambda _: True)
def handle_message(message):
    # if message.from_user.username in config.users:
    response = openai.Completion.create(
        model='text-davinci-003',
        prompt=message.text,
        temperature=0.5,
        max_tokens=2000,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
    )

    print('\n - user: ', message.from_user.username)
    print(' - question: ', message.text)
    print(' - response: ', response)
    bot.send_message(chat_id=message.from_user.id, text=f"{response['choices'][0]['text']}")
    # else:
    #     bot.send_message(chat_id=message.from_user.id, text=f" - у {message.from_user.username} нет доступа!")


def telegram_polling():
    try:
        bot.polling(none_stop=True)
    except:
        traceback_error_string = traceback.format_exc()
        # print('\r\n<<ERROR polling>>\r\n')
        print("\r\n\r\n" + time.strftime(
            "%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string + "\r\n<<ERROR polling>>")
        with open(config.file_error_log, "a") as myfile:
            myfile.write("\r\n\r\n" + time.strftime(
                "%c") + "\r\n<<ERROR polling>>\r\n" + traceback_error_string + "\r\n<<ERROR polling>>")
            # myfile.write("\r\n --- error polling ---, " + time.strftime("%c") + "\n")
        bot.stop_polling()
        time.sleep(3)
        telegram_polling()
        bot.send_message('1077463086', 'i fell 😕')


telegram_polling()
