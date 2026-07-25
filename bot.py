import config
import telebot
print(config.token)

bot = telebot.TeleBot(config.token)


# Обработка '/start' и '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """\
Привет, я EchoBot.
Я здесь, чтобы повторить твои добрые слова. Просто скажи что-нибудь приятное, и я скажу тебе то же самое!\
""")


# Обработка всех остальных сообщений с типом контента 'text' (по умолчанию для content_types используется ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()