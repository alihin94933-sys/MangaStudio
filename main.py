import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse
import os
from flask import Flask
import threading

# التوكن الخاص بك
BOT_TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

users_db = {}

# قاموس اللغات الاحترافي
texts = {
    'ar': {'welcome': "مرحباً بك! 🎨 لديك (1) صورة مجانية للتجربة.\nأرسل وصف الغلاف بالإنجليزية الآن.", 'wait': "⏳ جاري رسم غلافك الاحترافي... انتظر قليلاً.", 'done': "🎨 تفضل! هذا غلافك.\nرصيدك المتبقي: {}", 'err': "❌ عذراً، البرومت طويل جداً أو هناك ضغط على السيرفر.", 'saved': "✅ تم تفعيل اللغة العربية!"},
    'en': {'welcome': "Welcome! 🎨 You have (1) free credit.\nSend your cover description in English now.", 'wait': "⏳ Generating your professional cover... Please wait.", 'done': "🎨 Here is your cover!\nRemaining credits: {}", 'err': "❌ Error! Prompt too long or server busy.", 'saved': "✅ English activated!"},
    'es': {'welcome': "¡Bienvenido! 🎨 Tienes (1) crédito gratis.\nEnvía la descripción en inglés.", 'wait': "⏳ Generando...", 'done': "🎨 ¡Listo!\nCréditos: {}", 'err': "❌ Error en la generación.", 'saved': "✅ ¡Español activado!"},
    'fr': {'welcome': "Bienvenue ! 🎨 (1) crédit gratuit.\nEnvoyez la description en anglais.", 'wait': "⏳ Création...", 'done': "🎨 Terminé !\nCrédits : {}", 'err': "❌ Erreur de génération.", 'saved': "✅ Français activé !"},
    'ru': {'welcome': "Добро пожаловать! 🎨 1 бесплатная попытка.\nПришлите описание на английском.", 'wait': "⏳ Создание...", 'done': "🎨 Готово!\nОсталось: {}", 'err': "❌ Ошибка генерации.", 'saved': "✅ Русский активирован!"},
    'zh': {'welcome': "欢迎！🎨 您有1次免费机会。\n请用英文发送描述。", 'wait': "⏳ 生成中...", 'done': "🎨 完成！\n剩余额度：{}", 'err': "❌ 生成 error。", 'saved': "✅ 中文已激活！"},
    'hi': {'welcome': "नमस्ते! 🎨 आपके पास 1 फ्री क्रेडिट है।\nअंग्रेजी में विवरण भेजें।", 'wait': "⏳ बन रहा है...", 'done': "🎨 तैयार है!\nक्रेडिट: {}", 'err': "❌ त्रुटि हुई।", 'saved': "✅ हिंदी सक्रिय!"},
    'pt': {'welcome': "Bem-vindo! 🎨 Você tem 1 crédito grátis.\nEnvie a descrição em inglês.", 'wait': "⏳ Gerando...", 'done': "🎨 Pronto!\nCréditos: {}", 'err': "❌ Erro na geração.", 'saved': "✅ Português ativado!"},
    'ja': {'welcome': "ようこそ！🎨 1回無料です。\n英語で説明を送ってください。", 'wait': "⏳ 作成中...", 'done': "🎨 できました！\n残り: {}", 'err': "❌ エラーが発生しました。", 'saved': "✅ 日本語が設定されました！"},
    'de': {'welcome': "Willkommen! 🎨 1 Gratis-Credit.\nSende die Beschreibung auf Englisch.", 'wait': "⏳ Generierung...", 'done': "🎨 Fertig!\nCredits: {}", 'err': "❌ Fehler aufgetreten.", 'saved': "✅ Deutsch aktiviert!"}
}

def lang_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(k.upper(), callback_data=f"lang_{k}") for k in texts.keys()]
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    users_db[chat_id] = {'credits': 1, 'lang': None}
    bot.send_message(chat_id, "🌍 Choose Language / اختر اللغة:", reply_markup=lang_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    users_db[chat_id]['lang'] = lang
    bot.edit_message_text(texts[lang]['saved'], chat_id, call.message.message_id)
    bot.send_message(chat_id, texts[lang]['welcome'])

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in users_db or not users_db[chat_id]['lang']:
        bot.send_message(chat_id, "🌍 Please choose language first:", reply_markup=lang_keyboard())
        return
    
    lang = users_db[chat_id]['lang']
    if users_db[chat_id]['credits'] > 0:
        generate_cover(chat_id, message.text, lang)
    else:
        bot.send_message(chat_id, "❌ No credits left / نفد الرصيد")

def generate_cover(chat_id, prompt, lang):
    bot.send_message(chat_id, texts[lang]['wait'])
    # تنظيف البرومت لضمان عدم فشل الرابط
    clean_prompt = prompt[:700] 
    encoded_prompt = urllib.parse.quote(clean_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true"
    
    try:
        bot.send_photo(chat_id, image_url, caption=texts[lang]['done'].format(users_db[chat_id]['credits'] - 1))
        users_db[chat_id]['credits'] -= 1
    except:
        bot.send_message(chat_id, texts[lang]['err'])

@app.route('/')
def index(): return "Global Manga Bot is Live!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def set_language(call):
    chat_id = call.message.chat.id
    lang_code = call.data.split("_")[1]
    users_db[chat_id]['lang'] = lang_code
    bot.edit_message_text(texts[lang_code]['saved'], chat_id, call.message.message_id)
    bot.send_message(chat_id, texts[lang_code]['welcome'])

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    if chat_id not in users_db or not users_db[chat_id].get('lang'):
        bot.send_message(chat_id, "Choose language:", reply_markup=lang_keyboard())
        return
    lang = users_db[chat_id]['lang']
    if users_db[chat_id]['credits'] > 0:
        generate_cover(chat_id, message.text, lang)
    else:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(texts[lang]['btn'], callback_data="buy_5_pack"))
        bot.send_message(chat_id, texts[lang]['empty'], reply_markup=markup)

def generate_cover(chat_id, prompt, lang):
    bot.send_message(chat_id, texts[lang]['wait'])
    encoded_prompt = urllib.parse.quote(prompt + " manga cover, anime style, masterpiece")
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true"
    try:
        bot.send_photo(chat_id, image_url, caption=texts[lang]['done'].format(users_db[chat_id]['credits'] - 1))
        users_db[chat_id]['credits'] -= 1
    except:
        bot.send_message(chat_id, texts[lang]['err'])

@bot.callback_query_handler(func=lambda call: call.data == "buy_5_pack")
def process_buy(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "نظام الدفع قيد التفعيل.. جرب النسخة المجانية حالياً!")

@app.route('/')
def index():
    return "Bot is Live!"

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
