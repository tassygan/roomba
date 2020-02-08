import telebot
import cloudinary
import urllib3
import requests
from telebot import types
from PIL import Image
from io import StringIO
from telebot import types
from database import SQL
from search import Search, Tenant

cloudinary.config(
  cloud_name = 'hbvb8qfy3',  
  api_key = '565397896233387',  
  api_secret = 'ADPpwUIj-9-_NFCR7FyM6OP-jY4'  
)

db = SQL()

search = Search()

token = "1012837410:AAFY0lxwBFgWPIbRO-lO_MumXnlYJl-1ReQ"
bot = telebot.TeleBot(token)
photo_id = ""

@bot.message_handler(commands = ['start'])
def photo_rep(message):
	global photo_id
	#photo_url = cloudinary.CloudinaryImage("samples/people/bicycle.jpg").build_url()
	#img = Image.open(urllib3.urlopen(photo_url))
	#bot.send_photo(message.chat.id, img)
	bot.send_message(message.chat.id, 'Hello! Send me a photo')

@bot.message_handler(content_types = ['photo'])
def send_photo(message):
	global photo_id
	bot.send_photo(message.chat.id, message.photo)
	keyboard = types.InlineKeyboardMarkup()
	button = types.InlineButtonMarkup('Get photo', callback_data = 'photo')

@bot.message_handler(func=lambda call:True)
def photo(call):
	global photo_id
	img = open(photo_id, 'rb')
	bot.send_photo(call.message.chat.id, img)

bot.polling(none_stop = True)