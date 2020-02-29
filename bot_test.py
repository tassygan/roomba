from __future__ import print_function
import telebot
import time
import urllib
from telebot import types
from telebot.types import InputMediaPhoto
import photos

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
	try:
	    chat_id = message.chat.id

	    file_info = bot.get_file(message.photo[-1].file_id)
	    downloaded_file = bot.download_file(file_info.file_path)

	    src = message.photo[-1].file_name;
	    with open(src, 'wb') as new_file:
	        new_file.write(downloaded_file)

	    bot.reply_to(message, "Пожалуй, я сохраню это")
	except Exception as e:
	    bot.reply_to(message, e)
@bot.message_handler(func=lambda commands:True)
def check(message):
	bot.send_message(message.chat.id, message.text[:6])

bot.polling()