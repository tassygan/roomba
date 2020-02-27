from __future__ import print_function
import telebot
import time
import urllib
from telebot import types
from telebot.types import InputMediaPhoto
import photos

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_photo(message):
	file_id = '17RntL3FT86ikmHMhQbm2Grupy2bJvMe3'
	fh = photos.download_photo(file_id)
	bot.send_photo(message.chat.id, fh)
bot.polling()
while True:
    time.sleep(0)