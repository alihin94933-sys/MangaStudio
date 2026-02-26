import telebot
import urllib.parse
import time

# التوكن الخاص بك
BOT_TOKEN = '8701895099:AAF94_5mP41AuP3IoyZiBVLau19Zm0dy8v4'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "مرحباً بك في استوديو الأغلفة السحابي! 🚀🎨\nأرسل وصفك بالإنجليزية الآن.")

@bot.message_handler(func=lambda message: True)
def generate(message):
    bot.send_chat_action(message.chat.id, 'upload_photo')
    safe_prompt = urllib.parse.quote(message.text)
    # محرك الرسم السريع Flux
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&model=flux&seed={int(time.time())}"
    
    try:
        # إرسال الصورة عبر الرابط مباشرة لضمان السرعة في السودان
        bot.send_photo(message.chat.id, image_url, caption="تم التصميم بواسطة السيرفر بنجاح! 🔥")
    except:
        bot.send_message(message.chat.id, f"تفضل رابط التصميم المباشر:\n{image_url}")

bot.polling(none_stop=True)
