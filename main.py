import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse
import os
import requests
import io
from flask import Flask
import threading

# التوكن الخاص بك
BOT_TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# تتبع حالة المستخدم (اللغة والنوع المختاد)
user_states = {}

# نصوص البوت بـ 10 لغات (ركزت لك على العربية والإنجليزية هنا لضمان دقة المسافات)
texts = {
    'ar': {
        'start': "مرحباً بك في بوت تصميم أغلفة الأنمي والمانجا الاحترافي! 🎨\n\nالرجاء اختيار لغتك المفضلة أولاً:",
        'genre': "اختيار رائع! الآن حدد تصنيف الغلاف (Genre) لضبط الأجواء:",
        'prompt': "ممتاز! أرسل الآن وصفك للغلاف بالإنجليزية.\n\n💡 **نصيحة ذهبية:** يمكنك تضمين رابط صورة مرجعية في رسالتك، وسأقوم بمحاولة محاكاتها!",
        'wait': "⏳ جاري معالجة طلبك (نوع: {})... يتم الآن رسم الغلاف بدقة عالية، يرجى الانتظار.",
        'done': "🎨 تم الانتهاء! إليك غلافك الاحترافي:",
        'error': "❌ نعتذر، حدث ضغط على السيرفر. حاول إرسال الوصف مرة أخرى.",
        'genres': ["أكشن 👊", "رومانسي ❤️", "رعب 💀", "شونين 🔥", "سينين 🌑"]
    },
    'en': {
        'start': "Welcome to the Professional Anime & Manga Cover Designer! 🎨\n\nPlease choose your language:",
        'genre': "Great choice! Now, select the cover genre to set the mood:",
        'prompt': "Excellent! Send your description in English.\n\n💡 **Pro Tip:** You can include a reference image link in your prompt for better results!",
        'wait': "⏳ Processing your ({}) request... Drawing the cover in high quality, please wait.",
        'done': "🎨 Done! Here is your professional cover:",
        'error': "❌ Sorry, the server is busy. Please try sending the description again.",
        'genres': ["Action 👊", "Romance ❤️", "Horror 💀", "Shonen 🔥", "Seinen 🌑"]
    }
}

# --- لوحات المفاتيح ---
def get_lang_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
               InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"))
    return markup

def get_genre_keyboard(lang):
    markup = InlineKeyboardMarkup(row_width=2)
    genres = texts[lang]['genres']
    btns = [InlineKeyboardButton(g, callback_data=f"genre_{g}") for g in genres]
    markup.add(*btns)
    return markup

# --- معالجة الأوامر ---
@bot.message_handler(commands=['start'])
def welcome_message(message):
    chat_id = message.chat.id
    user_states[chat_id] = {'lang': None, 'genre': None}
    bot.send_message(chat_id, texts['ar']['start'], reply_markup=get_lang_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language(call):
    chat_id = call.message.chat.id
    lang = call.data.split('_')[1]
    user_states[chat_id]['lang'] = lang
    bot.edit_message_text(texts[lang]['genre'], chat_id, call.message.message_id, reply_markup=get_genre_keyboard(lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def handle_genre(call):
    chat_id = call.message.chat.id
    genre = call.data.split('_')[1]
    user_states[chat_id]['genre'] = genre
    lang = user_states[chat_id]['lang']
    bot.edit_message_text(texts[lang]['prompt'], chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def process_generation(message):
    chat_id = message.chat.id
    if chat_id not in user_states or not user_states[chat_id]['genre']:
        bot.send_message(chat_id, "من فضلك ابدأ بالضغط على /start أولاً.")
        return

    lang = user_states[chat_id]['lang']
    genre = user_states[chat_id]['genre']
    prompt = message.text

    bot.send_message(chat_id, texts[lang]['wait'].format(genre))
    
    # دمج النوع مع البرومت لتحسين النتائج
    final_prompt = f"{genre} style anime manga cover, {prompt}, high detail, professional illustration"
    encoded_query = urllib.parse.quote(final_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_query}?width=1024&height=1536&nologo=true&seed={chat_id}"

    try:
        # تحميل الصورة من السيرفر كبيانات خام
        response = requests.get(image_url, timeout=40)
        if response.status_code == 200:
            # إرسالها كصورة حقيقية (Photo) وليس ملفاً
            image_data = io.BytesIO(response.content)
            bot.send_photo(chat_id, image_data, caption=texts[lang]['done'])
        else:
            bot.send_message(chat_id, texts[lang]['error'])
    except:
        bot.send_message(chat_id, texts[lang]['error'])

# خادم الويب لـ Render
@app.route('/')
def home(): return "Bot is Online!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    }
}

# لوحة اختيار اللغة
def lang_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🇸🇦 العربية", callback_data="setlang_ar"),
               InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"))
    return markup

# لوحة اختيار النوع
def genre_markup(lang):
    markup = InlineKeyboardMarkup(row_width=2)
    genres = texts[lang]['genres']
    btns = [InlineKeyboardButton(g, callback_data=f"setgenre_{g}") for g in genres]
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    users_db[chat_id] = {'lang': None, 'genre': None}
    bot.send_message(chat_id, "مرحباً بك في بوت تصميم أغلفة الأنمي والمانجا! 🎨\nWelcome to Anime & Manga Cover Designer!", reply_markup=lang_markup())

@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def callback_lang(call):
    chat_id = call.message.chat.id
    lang = call.data.split("_")[1]
    users_db[chat_id]['lang'] = lang
    bot.edit_message_text(texts[lang]['choose_genre'], chat_id, call.message.message_id, reply_markup=genre_markup(lang))

@bot.callback_query_handler(func=lambda call: call.data.startswith("setgenre_"))
def callback_genre(call):
    chat_id = call.message.chat.id
    genre = call.data.split("_")[1]
    users_db[chat_id]['genre'] = genre
    lang = users_db[chat_id]['lang']
    bot.edit_message_text(texts[lang]['ask_prompt'], chat_id, call.message.message_id)

@bot.message_handler(func=lambda message: True)
def handle_prompt(message):
    chat_id = message.chat.id
    if chat_id not in users_db or not users_db[chat_id]['genre']:
        bot.send_message(chat_id, "من فضلك ابدأ بالضغط على /start")
        return

    lang = users_db[chat_id]['lang']
    genre = users_db[chat_id]['genre']
    prompt = message.text

    bot.send_message(chat_id, texts[lang]['wait'].format(genre))
    
    # دمج النوع مع البرومت لضمان الدقة
    full_prompt = f"{genre} manga cover style, {prompt}, high resolution, masterpiece, colorful"
    encoded_prompt = urllib.parse.quote(full_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true&seed={chat_id}"

    try:
        # تحميل الصورة وإرسالها كملف صورة حقيقي
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            photo = io.BytesIO(response.content)
            bot.send_photo(chat_id, photo, caption=texts[lang]['done'])
        else:
            bot.send_message(chat_id, texts[lang]['err'])
    except Exception as e:
        bot.send_message(chat_id, texts[lang]['err'])

@app.route('/')
def home(): return "Manga Bot is running!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
.run(host="0.0.0.0", port=port)
