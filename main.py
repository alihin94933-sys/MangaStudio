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

# قاموس اللغات (10 لغات) مع رسائل واضحة للوصف الطويل
texts = {
    'ar': {'welcome': "مرحباً بك! 🎨 لديك (1) صورة مجانية.\nأرسل وصف الغلاف بالإنجليزية (مهما كان طويلاً).", 'wait': "⏳ جاري تحليل الوصف الضخم ورسم الغلاف... قد يستغرق ذلك وقتاً إضافياً للتفاصيل.", 'done': "🎨 تفضل! هذا غلافك الاحترافي.\nرصيدك: {}", 'err': "❌ الوصف ضخم جداً! حاول اختصاره قليلاً ليتحمله السيرفر.", 'saved': "✅ تم تفعيل العربية!"},
    'en': {'welcome': "Welcome! 🎨 (1) free credit.\nSend your description (no matter how long).", 'wait': "⏳ Analyzing long prompt and generating... Please wait.", 'done': "🎨 Here is your cover!\nCredits: {}", 'err': "❌ Prompt too long! Try a shorter version.", 'saved': "✅ English activated!"},
    'es': {'welcome': "¡Bienvenido! 🎨 1 crédito.\nEnvía la descripción larga.", 'wait': "⏳ Generando...", 'done': "🎨 ¡Listo!\nCréditos: {}", 'err': "❌ Texto demasiado largo.", 'saved': "✅ ¡Español!"},
    'fr': {'welcome': "Bienvenue ! 🎨 1 crédit.\nDescription longue acceptée.", 'wait': "⏳ Création...", 'done': "🎨 Terminé !\nCrédits : {}", 'err': "❌ Texte trop long.", 'saved': "✅ Français !"},
    'ru': {'welcome': "Привет! 🎨 1 попытка.\nПришлите длинное описание.", 'wait': "⏳ Создание...", 'done': "🎨 Готово!\nОсталось: {}", 'err': "❌ Ошибка: слишком длинный текст.", 'saved': "✅ Русский!"},
    'zh': {'welcome': "欢迎！🎨 1次机会。\n请发送您的长描述。", 'wait': "⏳ 生成中...", 'done': "🎨 完成！\n额度：{}", 'err': "❌ 错误：描述过长。", 'saved': "✅ 中文！"},
    'hi': {'welcome': "नमस्ते! 🎨 1 क्रेडिट।\nलंबा विवरण भेजें।", 'wait': "⏳ बन रहा है...", 'done': "🎨 तैयार!\nक्रेडिट: {}", 'err': "❌ विवरण बहुत लंबा है।", 'saved': "✅ हिंदी!"},
    'pt': {'welcome': "Bem-vindo! 🎨 1 crédito.\nEnvie a descrição longa.", 'wait': "⏳ Gerando...", 'done': "🎨 Pronto!\nCréditos: {}", 'err': "❌ Texto muito longo.", 'saved': "✅ Português!"},
    'ja': {'welcome': "ようこそ！🎨 1回無料。\n長い説明を送ってください。", 'wait': "⏳ 作成中...", 'done': "🎨 完了！\n残り: {}", 'err': "❌ プロンプトが長すぎます。", 'saved': "✅ 日本語！"},
    'de': {'welcome': "Willkommen! 🎨 1 Credit.\nLange Beschreibung senden.", 'wait': "⏳ Generierung...", 'done': "🎨 Fertig!\nCredits: {}", 'err': "❌ Fehler: Text zu lang.", 'saved': "✅ Deutsch!"}
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
    bot.send_message(chat_id, "🌍 Please choose language / اختر اللغة:", reply_markup=lang_keyboard())

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
        bot.send_message(chat_id, "🌍 Choose language first:", reply_markup=lang_keyboard())
        return
    
    lang = users_db[chat_id]['lang']
    if users_db[chat_id]['credits'] > 0:
        generate_cover(chat_id, message.text, lang)
    else:
        bot.send_message(chat_id, "❌ No credits left / نفد الرصيد")

def generate_cover(chat_id, prompt, lang):
    bot.send_message(chat_id, texts[lang]['wait'])
    
    # رفع الحد الأقصى للبرومت إلى 2000 حرف لضمان استيعاب كل التفاصيل
    safe_prompt = prompt[:2000] 
    encoded_prompt = urllib.parse.quote(safe_prompt)
    
    # إضافة enhance=true لزيادة الدقة في التفاصيل الكبيرة
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true&enhance=true"
    
    try:
        bot.send_photo(chat_id, image_url, caption=texts[lang]['done'].format(users_db[chat_id]['credits'] - 1))
        users_db[chat_id]['credits'] -= 1
    except Exception as e:
        print(f"Error: {e}")
        bot.send_message(chat_id, texts[lang]['err'])

@app.route('/')
def index(): return "The Beast Manga Bot is Live!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
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
