import telebot
import time
from telebot import types

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)

last_mess = ''

@bot.message_handler(commands = ['start'])
def start(message):
	global last_mess
	keyboard = types.InlineKeyboardMarkup()
	button1 = types.InlineKeyboardButton('<<123check')
	button2 = types.InlineKeyboardButton('123check>>')
	keyboard = ([button1, button2], )
	last_mess = bot.send_message(message.chat.id, 'Hello!', reply_markup=keyboard)
	time.sleep(5)
	bot.delete_message(message.chat.id, last_mess.message_id)

bot.polling(none_stop=True)