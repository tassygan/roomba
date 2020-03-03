from __future__ import print_function
import telebot
import time
import urllib
from telebot import types
from telebot.types import InputMediaPhoto

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
	chat_id = message.chat.id
	files = message.photo[-1].file_id.split()
	print(files)
	print(files[0])
	print(message.photo[-1].file_id[49:])
	#print(len(message.photo[-1].file_id)/2)
	file_info = bot.get_file(message.photo[-1].file_id[49:])
	downloaded_file = bot.download_file(file_info.file_path)

	src = message.photo[-1].file_name[:(len(message.photo[-1].file_name)/2)];
	with open(src, 'wb') as new_file:
	    new_file.write(downloaded_file)

	bot.reply_to(message, "Пожалуй, я сохраню это")

bot.polling()