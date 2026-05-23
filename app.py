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
        "nome": "dry m.f.l",
        "prezzo": "29.99 €",
        "video_url": "https://res.cloudinary.com/dg1axjftz/video/upload/v1779487727/10_drdrrd.mp4"
    },
    "2": {
        "nome": "📹 Corso Video Editing",
        "prezzo": "49.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    "3": {
        "nome": "🎨 Corso Graphic Design",
        "prezzo": "39.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    },
    "4": {
        "nome": "🤖 Corso Telegram Bot",
        "prezzo": "34.99 €",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    }
}

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

# ==================== MENU PRINCIPALE CON DUE PULSANTI ====================
def mostra_menu_principale(chat_id, nome_utente):
    """Mostra il menu principale con i due pulsanti: Vetrina e Contattaci"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bottoni = [
        telebot.types.KeyboardButton("🛍️ VETRINA"),
        telebot.types.KeyboardButton("📞 CONTATTACI")
    ]
    markup.add(*bottoni)
    
    bot.send_message(
        chat_id,
        f"🎉 *BENVENUTO NEL NEGOZIO FAMILY!* 🎉\n\n"
        f"Ciao {nome_utente}!\n\n"
        f"✨ *Cosa desideri fare?*\n\n"
        f"📦 *🛍️ VETRINA* - Guarda i nostri prodotti\n"
        f"💬 *📞 CONTATTACI* - Parla con il supporto\n\n"
        f"Scegli un'opzione premendo il pulsante qui sotto 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== COMANDO START ====================
@bot.message_handler(commands=['start'])
def start(message):
    """Mostra il menu principale all'avvio"""
    mostra_menu_principale(message.chat.id, message.from_user.first_name)

# ==================== GESTIONE PULSANTI PRINCIPALI ====================
@bot.message_handler(func=lambda message: message.text == "🛍️ VETRINA")
def vetrina_pulsante(message):
    """Apre la vetrina dei prodotti"""
    negozio(message)

@bot.message_handler(func=lambda message: message.text == "📞 CONTATTACI")
def contattaci_pulsante(message):
    """Mostra le informazioni di contatto"""
    markup = telebot.types.InlineKeyboardMarkup()
    bottone_contatto = telebot.types.InlineKeyboardButton(
        "📱 CONTATTA SU TELEGRAM", 
        url="https://t.me/tousername"
    )
    markup.add(bottone_contatto)
    
    bot.send_message(
        message.chat.id,
        f"📞 *CONTATTACI*\n\n"
        f"Per assistenza, informazioni o acquisti:\n\n"
        f"👤 *Supporto:* @tousername\n"
        f"✉️ *Email:* support@familybot.com\n"
        f"⏰ *Orari:* 9:00 - 18:00 (Lun-Ven)\n\n"
        f"💬 *Rispondiamo in pochi minuti!*\n\n"
        f"Clicca il bottone qui sotto per parlarci direttamente su Telegram 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ==================== GESTIONE ALTRI MESSAGGI ====================
@bot.message_handler(func=lambda message: True)
def gestisci_altri_messaggi(message):
    """Gestisce qualsiasi altro messaggio mostrando il menu principale"""
    if message.text not in ["🛍️ VETRINA", "📞 CONTATTACI"]:
        mostra_menu_principale(message.chat.id, message.from_user.first_name)

# ==================== COMANDI BASE ====================
@bot.message_handler(commands=['help'])
def help_cmd(message):
    testo = """
🤖 *COMANDI DISPONIBILI*

/start - Mostra il menu principale
/help - Questo messaggio
/time - Orario attuale
/echo <testo> - Ripete il tuo messaggio
/random - Numero casuale (1-100)
/negozio - Apre la vetrina prodotti
/shop - Alternativa a /negozio

📦 *Comandi vetrina:*
- Clicca sui prodotti per vedere i dettagli
- Usa i bottoni per navigare

💡 *Usa i pulsanti nella tastiera!*
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
            text=f"📦 {prodotto['nome']} - {prodotto['prezzo']}",
            callback_data=f"prod_{id_prodotto}"
        )
        markup.add(bottone)
    
    # Aggiungi bottone per tornare al menu principale
    bottone_menu = telebot.types.InlineKeyboardButton(
        "🏠 MENU PRINCIPALE",
        callback_data="menu_principale"
    )
    markup.add(bottone_menu)
    
    bot.send_message(
        message.chat.id,
        "🛍️ *✨ NOSTRI PRODOTTI ✨*\n\nScegli un prodotto per vedere i dettagli:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def gestisci_click(call):
    """Gestisce tutti i click sui bottoni inline"""
    
    # CASO: Torna al menu principale
    if call.data == "menu_principale":
        mostra_menu_principale(call.message.chat.id, call.from_user.first_name)
        bot.answer_callback_query(call.id)
        return
    
    # CASO 1: L'utente ha cliccato su un prodotto
    if call.data.startswith("prod_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        testo = f"""
*📦 {prodotto['nome']}*

💰 *Prezzo:* {prodotto['prezzo']}
        """
        
        markup = telebot.types.InlineKeyboardMarkup(row_width=2)
        bottone_acquista = telebot.types.InlineKeyboardButton(
            "✅ ACQUISTA ORA", 
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
                text=f"📦 {prodotto['nome']} - {prodotto['prezzo']}",
                callback_data=f"prod_{id_prodotto}"
            )
            markup.add(bottone)
        
        # Aggiungi bottone per tornare al menu principale
        bottone_menu = telebot.types.InlineKeyboardButton(
            "🏠 MENU PRINCIPALE",
            callback_data="menu_principale"
        )
        markup.add(bottone_menu)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🛍️ *✨ NOSTRI PRODOTTI ✨*\n\nScegli un prodotto:",
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
    
    # CASO 4: L'utente ha cliccato "Acquista"
    elif call.data.startswith("acquista_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        markup = telebot.types.InlineKeyboardMarkup()
        bottone_contatta = telebot.types.InlineKeyboardButton(
            "📞 CONTATTA IL VENDITORE",
            url="https://t.me/tousername"
        )
        markup.add(bottone_contatta)
        
        bot.send_message(
            call.message.chat.id,
            f"✅ *ORDINE RICEVUTO!* ✅\n\n"
            f"📦 *Prodotto:* {prodotto['nome']}\n"
            f"💰 *Totale:* {prodotto['prezzo']}\n\n"
            f"📝 *Come procedere:*\n"
            f"1️⃣ Clicca sul pulsante qui sotto\n"
            f"2️⃣ Invia il codice: *ORD-{id_prodotto}*\n"
            f"3️⃣ Riceverai le istruzioni per il pagamento\n\n"
            f"💳 *Metodi di pagamento accettati:*\n"
            f"• PayPal\n"
            f"• Bonifico\n"
            f"• Carta di credito\n\n"
            f"_Una volta confermato il pagamento, riceverai l'accesso immediato!_ 🚀",
            parse_mode="Markdown",
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id, "🛒 Prodotto aggiunto! Contatta il venditore per completare l'ordine")

# ==================== SERVER FLASK PER RENDER ====================
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Telegram attivo su Render! Apri il bot e vedrai i pulsanti VETRINA e CONTATTACI!"

@app.route('/health')
def health():
    return "OK", 200

def run_bot():
    print("🤖 Bot avviato su Render!")
    print("📦 Vetrina prodotti caricata con", len(PRODOTTI), "prodotti")
    print("🔘 Pulsanti disponibili: VETRINA e CONTATTACI")
    print("💡 Usa /start per vedere il menu principale")
    bot.infinity_polling()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
