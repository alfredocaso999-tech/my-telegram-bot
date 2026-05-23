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
        "nome": "🍫DRY M.F.L🍫",
        "prezzo": "1g 10€ 5g 40€",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779487727/10_drdrrd.mp4"
    },
    "2": {
        "nome": "📹 Corso Video Editing",
        "prezzo": "49.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    "3": {
        "nome": " Corso Graphic Design",
        "prezzo": "39.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    "4": {
        "nome": " Corso Telegram Bot",
        "prezzo": "34.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
}

# ==================== USERNAME DEL VENDITORE ====================
USERNAME_VENDITORE = "tousername"  # CAMBIA CON IL TUO USERNAME! Es: "mariorossi"

# ==================== URL DELL'IMMAGINE ====================
URL_IMMAGINE = "https://i.postimg.cc/7Z1ZBCrp/IMG-0666.png"

# ==================== FUNZIONE PER SCARICARE VIDEO ====================
def scarica_video(url, filename="temp_video.mp4"):
    """Scarica un video da un URL e lo salva localmente"""
    try:
        response = requests.get(url, timeout=30, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        else:
            print(f"Errore download: status {response.status_code}")
            return None
    except Exception as e:
        print(f"Errore durante il download: {e}")
        return None

# ==================== COMANDO START CON IMMAGINE E PULSANTE ====================
@bot.message_handler(commands=['start'])
def start(message):
    """Messaggio di benvenuto con immagine e pulsante Vetrina"""
    
    # Crea il pulsante Vetrina
    markup = telebot.types.InlineKeyboardMarkup()
    bottone_vetrina = telebot.types.InlineKeyboardButton(
        "🛒 VETRINA", 
        callback_data="apri_vetrina"
    )
    markup.add(bottone_vetrina)
    
    # Testo da visualizzare (SOLO BENVENUTA FAMILY)
    testo = f"🩸 BENVENUTA FAMILY 🩸"
    
    # Invia immagine con didascalia e pulsante
    try:
        bot.send_photo(
            message.chat.id,
            URL_IMMAGINE,
            caption=testo,
            parse_mode="Markdown",
            reply_markup=markup
        )
        print(f"✅ Immagine inviata: {URL_IMMAGINE}")
    except Exception as e:
        print(f"❌ Errore nell'invio dell'immagine: {e}")
        # Se l'immagine non si carica, invia solo il testo
        bot.send_message(
            message.chat.id,
            "🩸 BENVENUTA FAMILY 🩸",
            parse_mode="Markdown",
            reply_markup=markup
        )

# ==================== COMANDI BASE ====================
@bot.message_handler(commands=['help'])
def help_cmd(message):
    testo = """
🤖 *COMANDI DISPONIBILI*

/start - Apre il negozio con immagine
/help - Questo messaggio
/time - Orario attuale
/echo <testo> - Ripete il tuo messaggio
/random - Numero casuale (1-100)
/negozio - Apre la vetrina prodotti
/shop - Alternativa a /negozio

📦 *Come acquistare:*
1️⃣ Clicca su VETRINA
2️⃣ Scegli un prodotto
3️⃣ Clicca su CONTATTACI
4️⃣ Clicca sul link per contattare il venditore
    """
    bot.reply_to(message, testo, parse_mode="Markdown")

@bot.message_handler(commands=['time'])
def time_cmd(message):
    bot.reply_to(message, datetime.now().strftime("⏰ %H:%M:%S - %d/%m/%Y"))

@bot.message_handler(commands=['echo'])
def echo_cmd(message):
    text = message.text.replace('/echo', '').strip()
    if text:
        bot.reply_to(message, f"🔊 {text}")
    else:
        bot.reply_to(message, "❓ Cosa vuoi che ripeta? Usa: /echo <testo>")

@bot.message_handler(commands=['random'])
def random_cmd(message):
    num = random.randint(1, 100)
    bot.reply_to(message, f"🎲 Numero casuale: {num}")

# ==================== VETRINA / NEGOZIO ====================
@bot.message_handler(commands=['negozio', 'shop'])
def negozio(message):
    """Mostra la lista dei prodotti disponibili"""
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    
    for id_prodotto, prodotto in PRODOTTI.items():
        bottone = telebot.types.InlineKeyboardButton(
            text=f" {prodotto['nome']} - {prodotto['prezzo']}",
            callback_data=f"prod_{id_prodotto}"
        )
        markup.add(bottone)
    
    bot.send_message(
        message.chat.id,
        " *🦍 I NOSTRI PRODOTTI 🦍*",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== UNICO CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def gestisci_click(call):
    """Gestisce tutti i click sui bottoni inline"""
    
    # CASO: Apri vetrina
    if call.data == "apri_vetrina":
        negozio(call.message)
        bot.answer_callback_query(call.id)
        return
    
    # CASO 1: L'utente ha cliccato su un prodotto
    if call.data.startswith("prod_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        testo = f"""
* {prodotto['nome']}*

💰 *Prezzo:* {prodotto['prezzo']}
        """
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        bottone_acquista = telebot.types.InlineKeyboardButton(
            "📞 CONTATTACI", 
            callback_data=f"acquista_{id_prodotto}"
        )
        bottone_video = telebot.types.InlineKeyboardButton(
            "🎬 GUARDA VIDEO", 
            callback_data=f"video_{id_prodotto}"
        )
        bottone_indietro = telebot.types.InlineKeyboardButton(
            "◀️ TORNA AL CATALOGO", 
            callback_data="catalogo"
        )
        markup.add(bottone_acquista, bottone_video)
        markup.add(bottone_indietro)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=testo,
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # CASO 2: L'utente vuole tornare al catalogo
    elif call.data == "catalogo":
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for id_prodotto, prodotto in PRODOTTI.items():
            bottone = telebot.types.InlineKeyboardButton(
                text=f" {prodotto['nome']} - {prodotto['prezzo']}",
                callback_data=f"prod_{id_prodotto}"
            )
            markup.add(bottone)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=" *🦍 I NOSTRI PRODOTTI 🦍*\n\nScegli un prodotto:",
            parse_mode="Markdown",
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
    
    # CASO 3: L'utente vuole vedere il video
    elif call.data.startswith("video_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        bot.send_message(call.message.chat.id, "🎬 Sto preparando il video... un attimo di pazienza!")
        
        try:
            # Controlla se è un link YouTube
            if "youtube.com" in prodotto['video_url'] or "youtu.be" in prodotto['video_url']:
                bot.send_message(
                    call.message.chat.id,
                    f"🎬 *{prodotto['nome']}*\n\n📹 Link video: {prodotto['video_url']}\n💰 Prezzo: {prodotto['prezzo']}",
                    parse_mode="Markdown"
                )
            else:
                video_path = scarica_video(prodotto['video_url'])
                
                if video_path:
                    with open(video_path, 'rb') as video_file:
                        bot.send_video(
                            call.message.chat.id,
                            video_file,
                            caption=f"🎬 *{prodotto['nome']}*\n💰 {prodotto['prezzo']}",
                            parse_mode="Markdown",
                            supports_streaming=True,
                            timeout=60
                        )
                    os.remove(video_path)
                else:
                    bot.send_message(
                        call.message.chat.id,
                        f"🎬 *{prodotto['nome']}*\n\n💰 Prezzo: {prodotto['prezzo']}\n\nLink: {prodotto['video_url']}",
                        parse_mode="Markdown"
                    )
            
            bot.answer_callback_query(call.id, "🎬 Video inviato!")
            
        except Exception as e:
            print(f"Errore: {e}")
            bot.send_message(
                call.message.chat.id,
                f"❌ Errore video.\nLink: {prodotto['video_url']}",
                parse_mode="Markdown"
            )
            bot.answer_callback_query(call.id, "⚠️ Errore nel video")
    
    # CASO 4: L'utente ha cliccato "Contattaci" - Link diretto alla chat
    elif call.data.startswith("acquista_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        # Crea il link diretto per la chat
        link_chat = f"https://t.me/{USERNAME_VENDITORE}"
        
        # Invia messaggio con link cliccabile
        bot.send_message(
            call.message.chat.id,
            f"📞 *Contatta il venditore per {prodotto['nome']}* 💰 {prodotto['prezzo']}\n\n👉 [CLICCA QUI PER APRIRE LA CHAT]({link_chat})",
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, "📞 Link chat aperto!")

# ==================== SERVER FLASK PER RENDER ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram attivo su Render! Usa /start per iniziare!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("🤖 Bot avviato su Render!")
    print("📦 Vetrina prodotti caricata con", len(PRODOTTI), "prodotti")
    print(f"🖼️ Immagine di benvenuto: {URL_IMMAGINE}")
    print(f"👤 Username venditore: {USERNAME_VENDITORE}")
    print("🔘 Pulsante VETRINA sotto l'immagine")
    print("💡 Comandi disponibili: /start, /help, /negozio, /shop, /time, /random, /echo")
    bot.infinity_polling()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
