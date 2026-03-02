import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse, os, requests, io, threading
from flask import Flask

# 1. الإعدادات الأساسية
TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
user_data = {}

# 2. القاموس الشامل (أضفنا الغموض وكل الأنواع)
STR = {
    'ar': {
        'w': "مرحباً بك في بوت تصميم الأغلفة! 🎨\nأنا صديقك المساعد، اختر لغتك للبدء:",
        'g': "رائع! الآن اختر 'تصنيف' الغلاف (Genre):",
        'p': "ممتاز! أرسل الآن وصف الغلاف بالإنجليزية (وصف طويل أو مع رابط صورة مرجعية):",
        't': "⏳ جاري الرسم... انتظر ثوانٍ قليلة يا صديقي.",
        'd': "🎨 تفضل! هذا غلافك الاحترافي:",
        'e': "❌ عذراً، حاول مجدداً بوصف مختلف.",
        'list': [
            "أكشن 🔥", "رومانسي ❤️", "رعب 💀", 
            "غموض 🔍", "فانتازيا ✨", "خيال علمي 🤖", 
            "دراما 🎭", "كوميدي 😂", "رياضة ⚽",
            "شونين ⚔️", "سينين 🌑", "خارق للطبيعة 👻"
        ]
    },
    'en': {
        'w': "Welcome to the Cover Designer Bot! 🎨\nI'm your assistant, choose your language:",
        'g': "Great! Now choose the cover 'Genre':",
        'p': "Excellent! Send your description in English (Long prompts/links are okay):",
        't': "⏳ Generating... Please wait a few seconds.",
        'd': "🎨 Done! Here is your professional cover:",
        'e': "❌ Error, please try again.",
        'list': [
            "Action 🔥", "Romance ❤️", "Horror 💀", 
            "Mystery 🔍", "Fantasy ✨", "Sci-Fi 🤖", 
            "Drama 🎭", "Comedy 😂", "Sports ⚽",
            "Shonen ⚔️", "Seinen 🌑", "Supernatural 👻"
        ]
    }
}

# 3. الأزرار والمنطق البرمجي
def get_l_kb():
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton("العربية 🇸🇦", callback_data="l_ar"), 
          InlineKeyboardButton("English 🇬🇧", callback_data="l_en"))
    return m

def get_g_kb(l):
    m = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(g, callback_data=f"g_{g}") for g in STR[l]['list']]
    m.add(*btns)
    return m

@bot.message_handler(commands=['start'])
def welcome(m):
    user_data[m.chat.id] = {}
    bot.send_message(m.chat.id, STR['ar']['w'], reply_markup=get_l_kb())

@bot.callback_query_handler(func=lambda c: c.data.startswith('l_'))
def set_l(c):
    l = c.data.split('_')[1]
    user_data[c.message.chat.id]['l'] = l
    bot.edit_message_text(STR[l]['g'], c.message.chat.id, c.message.message_id, reply_markup=get_g_kb(l))

@bot.callback_query_handler(func=lambda c: c.data.startswith('g_'))
def set_g(c):
    g = c.data.split('_')[1]
    user_data[c.message.chat.id]['g'] = g
    l = user_data[c.message.chat.id]['l']
    bot.edit_message_text(STR[l]['p'], c.message.chat.id, c.message.message_id)

@bot.message_handler(func=lambda m: True)
def process(m):
    u = m.chat.id
    if u not in user_data or 'g' not in user_data[u]:
        bot.send_message(u, "أهلاً بك! الرجاء الضغط على /start للبدء.")
        return
    
    l, g = user_data[u]['l'], user_data[u]['g']
    bot.send_message(u, STR[l]['t'])
    
    # دمج النوع مع الوصف لضمان جودة غلاف حقيقية
    query = urllib.parse.quote(f"{g} manga cover, {m.text}, masterpiece, high detail, 8k")
    url = f"https://image.pollinations.ai/prompt/{query}?width=1024&height=1536&nologo=true"
    
    try:
        r = requests.get(url, timeout=55)
        if r.status_code == 200:
            bot.send_photo(u, io.BytesIO(r.content), caption=STR[l]['d'])
        else:
            bot.send_message(u, STR[l]['e'])
    except:
        bot.send_message(u, STR[l]['e'])

# 4. خادم الويب (تأكدنا أن return داخل الدالة)
@app.route('/')
def home():
    return "Bot is Active and Ready for Mystery!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    m.add(InlineKeyboardButton("العربية 🇸🇦", callback_data="l_ar"), 
          InlineKeyboardButton("English 🇬🇧", callback_data="l_en"))
    return m

def get_genres(lang):
    m = InlineKeyboardMarkup(row_width=2)
    btns = [InlineKeyboardButton(g, callback_data=f"g_{g}") for g in MSGS[lang]['list']]
    m.add(*btns)
    return m

# 4. مسار المحادثة (المنطق البرمجي)
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

# 5. التوليد والإرسال كصورة حقيقية (Photo)
@bot.message_handler(func=lambda m: True)
def drawing_process(m):
    uid = m.chat.id
    if uid not in user_data or 'g' not in user_data[uid]:
        bot.send_message(uid, "الرجاء الضغط على /start للبدء.")
        return
    
    l, g = user_data[uid]['l'], user_data[uid]['g']
    bot.send_message(uid, MSGS[l]['wait'])
    
    # دمج التصنيف مع الوصف لضمان جودة غلاف حقيقية
    final_prompt = f"{g} manga cover, {m.text}, masterpiece, high detail, 8k, vibrant colors"
    encoded = urllib.parse.quote(final_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1536&nologo=true"
    
    try:
        # تحميل الصورة في الذاكرة أولاً لضمان وصولها لتليجرام
        r = requests.get(url, timeout=45)
        if r.status_code == 200:
            image_stream = io.BytesIO(r.content)
            bot.send_photo(uid, image_stream, caption=MSGS[l]['done'])
        else:
            bot.send_message(uid, MSGS[l]['err'])
    except Exception as e:
        bot.send_message(uid, MSGS[l]['err'])

# تشغيل خادم ويب بسيط لإبقاء الخدمة حية في Render
@app.route('/')
def home(): return "Bot is Online and Ready!"

if __name__ == "__main__":
    threading.Thread(target=lambda: bot.polling(none_stop=True)).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
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
