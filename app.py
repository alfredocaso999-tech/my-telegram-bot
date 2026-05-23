# ==================== UNICO CALLBACK HANDLER ====================
@bot.callback_query_handler(func=lambda call: True)
def gestisci_click(call):
    """Gestisce tutti i click sui bottoni inline"""
    
    # DEBUG: stampa per vedere cosa arriva
    print(f"Callback ricevuto: {call.data}")
    
    # CASO: Apri vetrina (dal pulsante sotto l'immagine)
    if call.data == "apri_vetrina":
        # Modifica il messaggio invece di inviarne uno nuovo
        markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for id_prodotto, prodotto in PRODOTTI.items():
            bottone = telebot.types.InlineKeyboardButton(
                text=f"📦 {prodotto['nome']} - {prodotto['prezzo']}",
                callback_data=f"prod_{id_prodotto}"
            )
            markup.add(bottone)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🛍️ *🦍 I NOSTRI PRODOTTI 🦍*\n\nScegli un prodotto:",
            parse_mode="Markdown",
            reply_markup=markup
        )
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
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🛍️ *🦍 I NOSTRI PRODOTTI 🦍*\n\nScegli un prodotto:",
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
            # Per link YouTube è meglio inviare solo il link
            if "youtube.com" in prodotto['video_url'] or "youtu.be" in prodotto['video_url']:
                bot.send_message(
                    call.message.chat.id,
                    f"🎬 *{prodotto['nome']}*\n\n📹 Video: {prodotto['video_url']}\n💰 Prezzo: {prodotto['prezzo']}",
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
    
    # CASO 4: L'utente ha cliccato "Acquista"
    elif call.data.startswith("acquista_"):
        id_prodotto = call.data.split("_")[1]
        prodotto = PRODOTTI[id_prodotto]
        
        markup = telebot.types.InlineKeyboardMarkup()
        bottone_contatta = telebot.types.InlineKeyboardButton(
            "📞 CONTATTA IL VENDITORE",
            url="https://t.me/tousername"  # CAMBIA CON IL TUO USERNAME!
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
