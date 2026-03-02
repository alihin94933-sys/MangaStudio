import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse, os, requests, io, threading
from flask import Flask

# 1. إعدادات البوت (التوكن الخاص بك)
TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# 2. القاموس (عربي وإنجليزي فقط لضمان الثبات)
MSGS = {
    'ar': {
        'start': "مرحباً بك في بوت تصميم أغلفة الأنمي والمانجا! 🎨\n\nأنا صديقك المساعد، اختر لغتك للبدء:",
        'genre': "رائع! الآن اختر 'جو' الغلاف (التصنيف):",
        'ask': "ممتاز! أرسل الآن وصف الغلاف بالإنجليزية.\n\n💡 نصيحة: يمكنك وضع رابط صورة مرجعية في رسالتك!",
        'wait': "⏳ جاري الرسم بدقة عالية... انتظر ثوانٍ قليلة.",
        'done': "🎨 تفضل يا صديقي! هذا هو غلافك الاحترافي:",
        'err': "❌ السيرفر مشغول قليلاً، حاول مجدداً الآن!",
        'list': ["أكشن 👊", "رومانسي ❤️", "رعب 💀", "شونين 🔥", "سينين 🌑"]
    },
    'en': {
        'start': "Welcome to Anime & Manga Cover Designer! 🎨\n\nChoose your language to start:",
        'genre': "Great! Now choose the cover genre:",
        'ask': "Excellent! Send your description in English.\n\n💡 Tip: You can include a reference image link!",
        'wait': "⏳ Generating in high quality... Please wait.",
        'done': "🎨 Done! Here is your professional cover:",
        'err': "❌ Server busy, please try again now!",
        'list': ["Action 👊", "Romance ❤️", "Horror 💀", "Shonen 🔥", "Seinen 🌑"]
    }
}

# 3. الأزرار
def get_langs():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("العربية 🇸🇦", callback_data="l_ar"), 
          InlineKeyboardButton("English 🇬🇧", callback_data="l_en"))
    return m

def get_genres(lang):
    m = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(g, callback_data=f"g_{g}") for g in MSGS[lang]['list']]
    m.add(*btns)
    return m

# 4. مسار المحادثة
@bot.message_handler(commands=['start'])
def welcome(m):
    user_data[m.chat.id] = {}
    bot.send_message(m.chat.id, MSGS['ar']['start'], reply_markup=get_langs())

@bot.callback_query_handler(func=lambda c: c.data.startswith('l_'))
def set_l(c):
    l = c.data.split('_')[1]
    user_data[c.message.chat.id]['l'] = l
    bot.edit_message_text(MSGS[l]['genre'], c.message.chat.id, c.message.message_id, reply_markup=get_genres(l))

@bot.callback_query_handler(func=lambda c: c.data.startswith('g_'))
def set_g(c):
    g = c.data.split('_')[1]
    user_data[c.message.chat.id]['g'] = g
    l = user_data[c.message.chat.id]['l']
    bot.edit_message_text(MSGS[l]['ask'], c.message.chat.id, c.message.message_id)

# 5. السحر (التوليد والإرسال كصورة حقيقية)
@bot.message_handler(func=lambda m: True)
def drawing_process(m):
    uid = m.chat.id
    if uid not in user_data or 'g' not in user_data[uid]:
        bot.send_message(uid, "الرجاء الضغط على /start للبدء.")
        return
    
    l, g = user_data[uid]['l'], user_data[uid]['g']
    bot.send_message(uid, MSGS[l]['wait'])
    
    # تحضير الرابط
    final_prompt = f"{g} manga cover, {m.text}, masterpiece, high detail, 8k"
    encoded = urllib.parse.quote(final_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1536&nologo=true"
    
    try:
        # تحميل وإرسال
        r = requests.get(url, timeout=40)
        if r.status_code == 200:
            bot.send_photo(uid, io.BytesIO(r.content), caption=MSGS[l]['done'])
        else:
            bot.send_message(uid, MSGS[l]['err'])
    except:
        bot.send_message(uid, MSGS[l]['err'])

# تشغيل الخادم
@app.route('/')
def home(): return "Bot is Alive and Happy!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
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
