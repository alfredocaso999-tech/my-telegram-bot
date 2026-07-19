import telebot
import os
import random
import requests
from datetime import datetime
import threading
from flask import Flask

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    print("❌ ERRORE: Imposta BOT_TOKEN nelle variabili d'ambiente")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# ==================== PRODOTTI DELLA VETRINA ====================
PRODOTTI = {
     "1": {
        "nome": "🇨🇦CANDY RUNTZ🇨🇦",
        "prezzo": "0.90 10€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1782903449/11_fvagmg.mp4"
    },
    "2": {
        "nome": "🇺🇸SNOWBALL🇺🇸",
        "prezzo": "0.80g 10€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779555745/4_bhqgac.mp4"
    },
    "3": {
        "nome": "🍫MOUSSE🍫",
        "prezzo": "2g 10€ 5g 20€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779706002/5_tvcxfq.mp4"
    },
    "4": {
        "nome": "🍫DRY FRESH🍫",
        "prezzo": "5g 30€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1783451780/2_n4hduq.mp4"
    },
    "5": {
        "nome": "🍫DRY OREO PANCAKES🍫",
        "prezzo": "1g 10€ 5g 35€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1783646156/7_oja1rm.mp4"
    },
    "6": {
        "nome": "🍫DRY KINDER BUFALO PLEIN🍫",
        "prezzo": "1g 10€ 5g 35€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1783477577/6_g8hp11.mp4"
     },
    "7": {
        "nome": "🍫FROZEN AURA FARMZ🍫",
        "prezzo": "1g 15€ 5g 60€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1784426556/12_yiqam3.mp4"
     },
    "8": {
        "nome": "🍫FROZEN BUFALO PLEIN🍫",
        "prezzo": "1g 15€ 5g 60€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1782044166/5_qjoav4.mp4"
     },
    "9": {
        "nome": "🍫FROZEN PINK LIMEZ🍫",
        "prezzo": "1g 15€ 5g 70€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1783345401/6_vv51kk.mp4"
    },
    "10": {
        "nome": "🍫FROZEN ZOWHAYA🍫",
        "prezzo": "1g 15€ 5g 70€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1783345326/14_lbvceq.mp4"
    },
    "11": {
        "nome": "🍫FROZEN MELLOW MANIA🍫",
        "prezzo": "1g 15€ 5g 70€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779706287/9_kbx3eq.mp4"
    },
    "12": {
        "nome": "🍫OVULO STATIC M.G🍫",
        "prezzo": "1g 20€ 5g 100€🎁2g 35€ 10g 180€🎁",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779706183/8_odpehx.mp4"
    }
}

# ==================== USERNAME DEL VENDITORE ====================
USERNAME_VENDITORE = "the_true_freedom"

# ==================== URL DELL'IMMAGINE ====================
URL_IMMAGINE = "https://i.postimg.cc/7Z1ZBCrp/IMG-0666.png"

# ==================== COMANDO START ====================
@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    bottone_vetrina = telebot.types.InlineKeyboardButton("🛒 VETRINA", callback_data="apri_vetrina")
    markup.add(bottone_vetrina)
    
    testo = f"🩸 BENVENUTA FAMILY 🩸"
    
    try:
        bot.send_photo(message.chat.id, URL_IMMAGINE, caption=testo, parse_mode="Markdown", reply_markup=markup)
    except Exception as e:
        bot.send_message(message.chat.id, "🩸 BENVENUTA FAMILY 🩸", parse_mode="Markdown", reply_markup=markup)

# ==================== COMANDI BASE ====================
@bot.message_handler(commands=['help'])
def help_cmd(message):
    testo = """
🤖 *COMANDI DISPONIBILI*

/start - Apre il negozio
/help - Questo messaggio
/time - Orario attuale
/negozio - Apre la vetrina prodotti

📦 *Come acquistare:*
1️⃣ Clicca su VETRINA
2️⃣ Scegli un prodotto
3️⃣ Clicca su CONTATTACI
    """
    bot.reply_to(message, testo, parse_mode="Markdown")

@bot.message_handler(commands=['time'])
def time_cmd(message):
    bot.reply_to(message, datetime.now().strftime("⏰ %H:%M:%S - %d/%m/%Y"))

@bot.message_handler(commands=['negozio', 'shop'])
def negozio(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for id_prodotto, prodotto in PRODOTTI.items():
        bottone = telebot.types.InlineKeyboardButton(
            text=f" {prodotto['nome']} - {prodotto['prezzo']}",
            callback_data=f"prod_{id_prodotto}"
        )
        markup.add(bottone)
    
    bot.send_message(message.chat.id, " *🦍 I NOSTRI PRODOTTI 🦍*", parse_mode="Markdown", reply_markup=markup)

# ==================== CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def gestisci_click(call):
    if call.data == "apri_vetrina":
        negozio(call.message)
        bot.answer_callback_query(call.id)
        return
    
    if call.data.startswith("prod_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        testo = f"\n* {prodotto['nome']}*\n\n💰 *Prezzo:* {prodotto['prezzo']}"
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        bottone_acquista = telebot.types.InlineKeyboardButton("📞 CONTATTACI", callback_data=f"acquista_{id_prodotto}")
        bottone_video = telebot.types.InlineKeyboardButton("🎬 GUARDA VIDEO", callback_data=f"video_{id_prodotto}")
        bottone_indietro = telebot.types.InlineKeyboardButton("◀️ TORNA AL CATALOGO", callback_data="catalogo")
        markup.add(bottone_acquista, bottone_video)
        markup.add(bottone_indietro)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=testo, parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    elif call.data == "catalogo":
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for id_prodotto, prodotto in PRODOTTI.items():
            bottone = telebot.types.InlineKeyboardButton(text=f" {prodotto['nome']} - {prodotto['prezzo']}", callback_data=f"prod_{id_prodotto}")
            markup.add(bottone)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=" *🦍 I NOSTRI PRODOTTI 🦍*\n\nScegli un prodotto:", parse_mode="Markdown", reply_markup=markup)
        bot.answer_callback_query(call.id)
    
    # 🎬 VIDEO - Usa un bottone inline con URL diretto
    elif call.data.startswith("video_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        # Crea un bottone che apre il video quando cliccato
        markup = telebot.types.InlineKeyboardMarkup()
        bottone_video = telebot.types.InlineKeyboardButton(
            "🎬 APRI VIDEO", 
            url=prodotto['video_url']  # Questo apre il link direttamente
        )
        bottone_indietro = telebot.types.InlineKeyboardButton(
            "◀️ TORNA INDIETRO", 
            callback_data="catalogo"
        )
        markup.add(bottone_video)
        markup.add(bottone_indietro)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🎬 *{prodotto['nome']}*\n\n💰 Prezzo: {prodotto['prezzo']}",
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    elif call.data.startswith("acquista_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        link_chat = f"https://t.me/{USERNAME_VENDITORE}"
        
        markup = telebot.types.InlineKeyboardMarkup()
        bottone_chat = telebot.types.InlineKeyboardButton("📞 APRI CHAT", url=link_chat)
        bottone_indietro = telebot.types.InlineKeyboardButton("◀️ TORNA INDIETRO", callback_data="catalogo")
        markup.add(bottone_chat)
        markup.add(bottone_indietro)
        
        # 🔥 RIGA CORRETTA (prima era sbagliata) 🔥
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"📞 *APRI CHAT PER PARLARE CON TRUE FREEDOM🦍* \n{prodotto['nome']}\n💰 Prezzo: {prodotto['prezzo']}",
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)

# ==================== SERVER FLASK ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram attivo su Render!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("🤖 Bot avviato su Render!")
    print("📦 Vetrina prodotti caricata con", len(PRODOTTI), "prodotti")
    print("✅ Video e chat con pulsanti cliccabili!")
    bot.infinity_polling()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
