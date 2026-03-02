import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse, os, requests, io, threading
from flask import Flask

# التوكن الخاص بك
BOT_TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
user_data = {}

# 1. قاموس النصوص (مبسط جداً لتجنب أخطاء الأقواس)
STR = {
    'ar': {
        'w': "مرحباً بك في بوت تصميم أغلفة الأنمي والمانجا! 🎨\nالرجاء اختيار لغتك:",
        'g': "اختر نوع الغلاف:",
        'p': "أرسل وصف الغلاف بالإنجليزية (يمكنك إضافة رابط صورة مرجعية):",
        't': "⏳ جاري الرسم... انتظر ثوانٍ.",
        'd': "🎨 تفضل! هذا غلافك الاحترافي:",
        'e': "❌ عذراً، حاول مجدداً بوصف أقصر.",
        'list': ["أكشن 🔥", "رومانسي ❤️", "رعب 💀", "شونين ✨", "سينين 🌑"]
    },
    'en': {
        'w': "Welcome to Anime & Manga Cover Bot! 🎨\nChoose your language:",
        'g': "Choose Genre:",
        'p': "Send description in English (You can add a reference link):",
        't': "⏳ Generating... Please wait.",
        'd': "🎨 Done! Here is your cover:",
        'e': "❌ Error, please try again.",
        'list': ["Action 🔥", "Romance ❤️", "Horror 💀", "Shonen ✨", "Seinen 🌑"]
    }
}

# 2. الأزرار
def get_langs():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("العربية 🇸🇦", callback_data="l_ar"), InlineKeyboardButton("English 🇬🇧", callback_data="l_en"))
    return m

def get_genres(l):
    m = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(g, callback_data=f"g_{g}") for g in STR[l]['list']]
    m.add(*btns)
    return m

# 3. المنطق (ترحيب -> لغة -> نوع)
@bot.message_handler(commands=['start'])
def start(m):
    user_data[m.chat.id] = {}
    bot.send_message(m.chat.id, STR['ar']['w'], reply_markup=get_langs())

@bot.callback_query_handler(func=lambda c: c.data.startswith('l_'))
def set_l(c):
    l = c.data.split('_')[1]
    user_data[c.message.chat.id]['l'] = l
    bot.edit_message_text(STR[l]['g'], c.message.chat.id, c.message.message_id, reply_markup=get_genres(l))

@bot.callback_query_handler(func=lambda c: c.data.startswith('g_'))
def set_g(c):
    g = c.data.split('_')[1]
    user_data[c.message.chat.id]['g'] = g
    l = user_data[c.message.chat.id]['l']
    bot.edit_message_text(STR[l]['p'], c.message.chat.id, c.message.message_id)

# 4. التوليد والإرسال كصورة حقيقية
@bot.message_handler(func=lambda m: True)
def draw(m):
    uid = m.chat.id
    if uid not in user_data or 'g' not in user_data[uid]: return
    
    l, g = user_data[uid]['l'], user_data[uid]['g']
    bot.send_message(uid, STR[l]['t'])
    
    query = urllib.parse.quote(f"{g} manga cover, {m.text}, masterpiece, 8k")
    url = f"https://image.pollinations.ai/prompt/{query}?width=1024&height=1536&nologo=true"
    
    try:
        r = requests.get(url, timeout=35)
        if r.status_code == 200:
            bot.send_photo(uid, io.BytesIO(r.content), caption=STR[l]['d'])
        else: bot.send_message(uid, STR[l]['e'])
    except: bot.send_message(uid, STR[l]['e'])

@app.route('/')
def h(): return "Bot is Live!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
