import openai
import config
import telebot
import requests
from telebot import types
import json
import traceback
import time
import os
from io import BytesIO
from PIL import Image
from datetime import datetime


openai.api_key = config.openai_apikey
bot = telebot.TeleBot(config.telegram_apikey)

bot.send_message('1077463086', 'i`m online 🫡')
thisFile = os.path.abspath(__file__)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я бот.')


@bot.message_handler(commands=['pic', 'картинка', 'фото', 'фотки', 'картинки', 'pics', 'photo', 'photos'])
def generator_pics(message):
    input = message.text.split()
    find_word = input[1:]
    print(' - user: ', message.from_user.username, ', ищет: ', find_word)
    time_start = datetime.now()

    response = openai.Image.create(
        prompt=str(find_word),
        n=3,
        size="1024x1024"
    )
    print('\n- response: ', response, '\n')
    time_end = datetime.now()
    time_request = time_start-time_end
    print(' - время запроса:', time_request)
    # image_url = response['data'][0]['url']

    for url in response['data']:
        link_photo = url['url']
        # img = open(link_photo, 'rb')
        bot.send_photo(message.chat.id, link_photo)
        # image_url = response['data']['url']
        # bot.send_message(message.chat.id, text=image_url)


@bot.message_handler(func=lambda _: True)
def handle_message(message):
    time_start = datetime.now()
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
    print(' - response: ', response['choices'][0]['text'])
    time_end = datetime.now()
    time_request = time_start-time_end
    print(' - время запроса:', time_request)
    bot.send_message(chat_id=message.from_user.id, text=f"{response['choices'][0]['text']}")
    # else:
    #     bot.send_message(chat_id=message.from_user.id, text=f" - у {message.from_user.username} нет доступа!")


@bot.message_handler(content_types=['document', 'photo'])
def document_and_photo(message):
    print(message.content_type)
    if message.content_type == 'document':
        fileID = message.document.file_id
    elif message.content_type == 'photo':
        fileID = message.photo[-1].file_id
        # print(fileID)

    print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    print('file.file_path =', file_info.file_path)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('temp/photo.png', 'wb') as new_file:
        new_file.write(downloaded_file)

    # Read the image file from disk and resize it
    image = Image.open("temp/photo.png")
    width, height = 256, 256
    image = image.resize((width, height))

    # Convert the image to a BytesIO object
    byte_stream = BytesIO()
    image.save(byte_stream, format='PNG')
    byte_array = byte_stream.getvalue()

    try:
        response = openai.Image.create_variation(
            image=byte_array,
            n=3,
            size="1024x1024"
        )
        for url in response['data']:
            link_photo = url['url']
            print(link_photo)
            bot.send_photo(message.chat.id, link_photo)
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)



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
