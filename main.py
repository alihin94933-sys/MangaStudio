import telebot
from telebot.types import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
import urllib.parse
import os
from flask import Flask
import threading

# التوكن الخاص بك تم إضافته هنا بنجاح
BOT_TOKEN = "8720479480:AAEoAnKxceXcESdMMAZqGBNGTKh5XImxXrU"
# توكن الدفع (سنتركه فارغاً الآن حتى تقوم بإعداده لاحقاً)
STRIPE_TOKEN = "" 

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# قاعدة بيانات وهمية لتتبع رصيد المستخدمين (Credits)
users_db = {}

# زر الشراء
def buy_keyboard():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💳 شراء باقة 5 صور (3$)", callback_data="buy_5_pack"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in users_db:
        # منح المستخدم صورة واحدة مجانية كرصيد ابتدائي
        users_db[chat_id] = {'credits': 1}
    
    welcome_text = (
        "مرحباً بك في بوت تصميم أغلفة المانجا الاحترافي! 🎨\n\n"
        "🎁 **لديك (1) صورة مجانية للتجربة!**\n"
        "بعدها يمكنك شراء باقة (5 صور بسعر 3$ فقط).\n\n"
        "للبدء، أرسل لي وصفاً للغلاف الذي تتخيله (باللغة الإنجليزية).\n"
        "مثال: A young anime hero holding a glowing sword in a dark forest"
    )
    bot.send_message(chat_id, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    
    # التأكد من تسجيل المستخدم إذا أرسل رسالة بدون الضغط على /start
    if chat_id not in users_db:
        users_db[chat_id] = {'credits': 1}

    # التحقق من توفر رصيد لدى المستخدم
    if users_db[chat_id]['credits'] > 0:
        generate_cover(chat_id, message.text)
    else:
        # إذا نفد الرصيد، نعرض عليه زر الشراء
        bot.send_message(
            chat_id, 
            "لقد نفد رصيدك من الصور المجانية. 😔\nيمكنك شراء باقة جديدة لمتابعة التصميم!", 
            reply_markup=buy_keyboard()
        )

def generate_cover(chat_id, prompt):
    bot.send_message(chat_id, "⏳ جاري رسم غلافك الاحترافي... يرجى الانتظار بضع ثوانٍ.")
    
    enhanced_prompt = prompt + " manga cover, anime style, highly detailed, masterpiece"
    encoded_prompt = urllib.parse.quote(enhanced_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1536&nologo=true"
    
    try:
        bot.send_photo(chat_id, image_url, caption="🎨 تفضل! هذا هو غلافك.")
        # خصم صورة واحدة من الرصيد بعد نجاح التوليد
        users_db[chat_id]['credits'] -= 1
        bot.send_message(chat_id, f"ℹ️ تبقى في رصيدك: {users_db[chat_id]['credits']} صور.")
    except Exception as e:
        bot.send_message(chat_id, "❌ عذراً، حدث خطأ من المصدر أثناء التوليد. لم يتم خصم رصيدك، حاول مجدداً بوصف مختلف.")

# --- نظام الدفع (Stripe) ---
@bot.callback_query_handler(func=lambda call: call.data == "buy_5_pack")
def process_buy(call):
    chat_id = call.message.chat.id
    
    if not STRIPE_TOKEN:
