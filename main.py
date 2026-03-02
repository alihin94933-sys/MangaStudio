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

users_db = {}

# قاموس النصوص واللغات
texts = {
    'ar': {
        'welcome': "مرحباً بك في بوت تصميم أغلفة الأنمي والمانجا! 🎨\nالرجاء اختيار لغتك المفضلة:",
        'choose_genre': "رائع! الآن اختر نوع الغلاف الذي تريده:",
        'ask_prompt': "ممتاز! أرسل الآن وصف الغلاف بالإنجليزية.\n💡 نصيحة: يمكنك وضع رابط صورة مرجعية في الوصف لنتائج أفضل!",
        'wait': "⏳ جاري تصميم غلافك (نوع: {})... يرجى الانتظار.",
        'done': "🎨 تفضل! هذا هو غلافك الاحترافي.",
        'err': "❌ حدث خطأ في الاتصال بسيرفر الصور، حاول مجدداً.",
        'genres': ["أكشن 👊", "رومانسي ❤️", "رعب 💀", "شونين 🔥", "سينين 🌑"]
    },
    'en': {
        'welcome': "Welcome to Anime & Manga Cover Designer! 🎨\nPlease choose your language:",
        'choose_genre': "Great! Now choose the genre of your cover:",
        'ask_prompt': "Excellent! Now send your description in English.\n💡 Tip: You can include a reference image link for better results!",
        'wait': "⏳ Designing your ({}) cover... Please wait.",
        'done': "🎨 Here is your professional cover.",
        'err': "❌ Error connecting to image server, please try again.",
        'genres': ["Action 👊", "Romance ❤️", "Horror 💀", "Shonen 🔥", "Seinen 🌑"]
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
