import telebot
from random import choice
import re
import os


API_TOKEN = '8875663395:AAH6J-j5RLmhFU4jGGwCfKAnC3WDAnLv3aY'

bot = telebot.TeleBot(API_TOKEN)

# Регулярное выражение для поиска ссылок (улучшенная версия)
URL_PATTERN = re.compile(r'https?://[^\s"\')>]+|www\.[^\s"\')>]+')

# Список заблокированных пользователей (в памяти, сбрасывается при перезапуске бота)
# В продакшене лучше использовать базу данных (SQLite, PostgreSQL)
banned_users = set()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Не отвечаем, если пользователь забанен
    if message.from_user.id in banned_users:
        return 
        
    bot.reply_to(
        message,
        "Привет, я EchoBot! 😊\n"
        "Я повторяю твои добрые слова. Просто скажи что-нибудь приятное!"
    )

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id in banned_users:
        return

    try:
        photo = message.photo[-1]
        bot.reply_to(message, f"📸 Получено фото! Размер: {photo.width}×{photo.height}")
    except Exception as e:
        print(f"Ошибка: {e}")

quotes = [
    "Мудрый человек требует всего лишь от себя, глупый — от других.",
    "Жизнь — это то, что с тобой происходит, пока ты строишь планы."
]

@bot.message_handler(content_types=['new_chat_members'])
def make_some(message):
    bot.send_message(message.chat.id, 'Новый участник!')
    bot.approve_chat_join_request(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['quote'])
def quote_handler(message):
    if message.from_user.id in banned_users:
        return
    random_quote = choice(quotes)
    bot.reply_to(message, f"🎓 Мудрая мысль: {random_quote}")

@bot.message_handler(func=lambda m: m.content_type == 'text')
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text

    # 1. Проверка: забанен ли пользователь?
    if user_id in banned_users:
        # Можно отправить скрытое сообщение или просто игнорировать
        return 

    # 2. Проверка на ссылку
    if URL_PATTERN.search(text):
        # Добавляем в список забаненных
        banned_users.add(user_id)
        
        response_text = (
            "⚠️ Ссылка обнаружена! 🚫\n\n"
            "Отправка ссылок запрещена правилами чата.\n"
            "Вы были заблокированы (забанены) в этом боте."
        )
        
        # Если это группа, можно использовать restrict_chat_member для жесткой блокировки
        if message.chat.type != 'private':
            try:
                # Запрещаем пользователю отправлять сообщения и медиа
                bot.restrict_chat_member(
                    chat_id=chat_id,
                    user_id=user_id,
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False
                )
                response_text += "\n\nАдминистратор также ограничил ваши права в группе."
            except Exception as e:
                print(f"Не удалось ограничить пользователя в группе: {e}")
                response_text += "\n\n(Не удалось автоматически ограничить права, так как у бота нет прав администратора)."

        bot.reply_to(message, response_text)
        return

    # Обычная обработка текста (если не бан и нет ссылки)
    bot.reply_to(message, f"Ты написал: {text}")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True, interval=0)
