import telebot
import urllib.parse
import time

# التوكن الخاص بك مدمج وجاهز للعمل
BOT_TOKEN = '8701895099:AAF94_5mP41AuP3IoyZiBVLau19Zm0dy8v4'
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "مرحباً بك في النسخة السحابية المستقرة! 🚀🎨\nأرسل وصف غلاف المانجا بالإنجليزية الآن.")

@bot.message_handler(func=lambda message: True)
def generate(message):
    # إشعار المستخدم بأن البوت بدأ الرسم
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # تنظيف النص لضمان عدم تعطل الرابط
    safe_prompt = urllib.parse.quote(message.text)
    
    # استخدام محرك Turbo المحدث لتجنب خطأ 1033 وضمان السرعة
    image_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&model=turbo&seed={int(time.time())}&nologo=true"
    
    try:
        # إرسال الصورة مباشرة عبر رابطها (هذه الطريقة هي الأنجح دائماً)
        bot.send_photo(message.chat.id, image_url, caption="تم التصميم بنجاح عبر المحرك العالمي! 🔥🎨")
    except:
        # في حال وجود ضغط شديد، يتم إرسال الرابط مباشرة للمستخدم
        bot.send_message(message.chat.id, f"تفضل رابط التصميم المباشر (اضغط عليه لمشاهدة الغلاف):\n{image_url}")

if __name__ == "__main__":
    print("البوت يعمل الآن بنسخة Turbo المستقرة على السحاب...")
    bot.polling(none_stop=True)
