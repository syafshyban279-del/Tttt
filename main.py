
import telebot
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ID = "YOUR_TELEGRAM_USER_ID"
API_KEY = "YOUR_AI_API_KEY"

# OpenAI API
client = OpenAI(api_key=API_KEY)

bot = telebot.TeleBot(TOKEN)

# حفظ سياق المحادثة
conversations = {}

SYSTEM_PROMPT = """
You are an advanced AI assistant.
You communicate in Arabic and other languages.
You help with programming, cybersecurity education,
technology, science, writing, translation and analysis.
Give accurate, detailed and useful answers.
Follow safety boundaries.
"""

# =========================
# START COMMAND
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    if str(message.from_user.id) != ID:
        bot.reply_to(message, "غير مصرح لك باستخدام هذا البوت.")
        return

    conversations[message.chat.id] = []

    bot.reply_to(
        message,
        "مرحباً بك في مساعد الذكاء الاصطناعي.\n\n"
        "أرسل سؤالك وسأجيبك.\n"
        "استخدم /reset لمسح المحادثة."
    )


# =========================
# RESET COMMAND
# =========================

@bot.message_handler(commands=['reset'])
def reset(message):

    if str(message.from_user.id) != ID:
        return

    conversations[message.chat.id] = []

    bot.reply_to(message, "تم بدء محادثة جديدة.")


# =========================
# AI CHAT
# =========================

@bot.message_handler(func=lambda message: True)
def ai_chat(message):

    if str(message.from_user.id) != ID:
        return

    chat_id = message.chat.id

    question = message.text

    if not question:
        return

    if chat_id not in conversations:
        conversations[chat_id] = []

    bot.send_chat_action(chat_id, "typing")

    try:

        history = conversations[chat_id]

        history.append({
            "role": "user",
            "content": question
        })

        # الاحتفاظ بآخر الرسائل
        history = history[-20:]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                *history
            ],
            temperature=0.7,
            max_tokens=2000
        )

        answer = response.choices[0].message.content

        history.append({
            "role": "assistant",
            "content": answer
        })

        conversations[chat_id] = history

        # تقسيم الردود الطويلة
        for i in range(0, len(answer), 4000):
            bot.send_message(
                chat_id,
                answer[i:i + 4000]
            )

    except Exception as e:

        print("AI ERROR:", str(e))

        bot.reply_to(
            message,
            "حدث خطأ أثناء الاتصال بالذكاء الاصطناعي."
        )


# =========================
# RUN BOT
# =========================

print("AI Telegram Bot Started Successfully")

bot.infinity_polling(
    skip_pending=True,
    timeout=30,
    long_polling_timeout=30
)
