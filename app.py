import telebot
import os
import random
from datetime import datetime
import threading
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    print("❌ ERRORE: Imposta BOT_TOKEN nelle variabili d'ambiente")
    exit(1)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, f"✅ Ciao {message.from_user.first_name}! Bot funzionante su Render!")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.reply_to(message, "Comandi: /start, /help, /time, /echo, /random")

@bot.message_handler(commands=['time'])
def time_cmd(message):
    bot.reply_to(message, datetime.now().strftime("⏰ %H:%M:%S"))

@bot.message_handler(commands=['echo'])
def echo_cmd(message):
    text = message.text.replace('/echo', '').strip()
    if text:
        bot.reply_to(message, f"🔊 {text}")

@bot.message_handler(commands=['random'])
def random_cmd(message):
    num = random.randint(1, 100)
    bot.reply_to(message, f"🎲 Numero casuale: {num}")

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram attivo su Render!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("🤖 Bot avviato su Render!")
    bot.infinity_polling()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)