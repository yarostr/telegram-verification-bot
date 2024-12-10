import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, filters
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, ConversationHandler
import time

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Константа для шага верификации
VERIFY_CONTACT = range(1)

# Множество для хранения пользователей, которые ещё не прошли верификацию
unverified_users = set()

# Обработка новых участников
def new_member(update: Update, context: CallbackContext):
    for new_user in update.message.new_chat_members:
        user_id = new_user.id
        first_name = new_user.first_name

        # Блокируем нового пользователя в чате
        context.bot.restrict_chat_member(update.message.chat_id, user_id, can_send_messages=False)

        # Отправляем сообщение с упоминанием пользователя
        update.message.reply_text(
            f"Привет, [{first_name}](tg://user?id={user_id})! "
            "Чтобы начать писать в чат, пройди верификацию. Нажми кнопку ниже для начала.",
            parse_mode="MarkdownV2",
            reply_markup=ReplyKeyboardMarkup([['Пройти верификацию']], one_time_keyboard=True)
        )

        # Добавляем пользователя в список не прошедших верификацию
        unverified_users.add(user_id)

# Обработка сообщений от пользователей
def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in unverified_users:
        update.message.delete()  # Удаляем сообщение пользователя
        update.message.reply_text(
            "Чтобы писать в чат, пройдите верификацию. Нажмите кнопку ниже для начала.",
            reply_markup=ReplyKeyboardMarkup([['Пройти верификацию']], one_time_keyboard=True)
        )

# Обработка команды /start
def start_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Чтобы пройти верификацию и получить возможность писать в чат, нажмите кнопку ниже.",
        reply_markup=ReplyKeyboardMarkup([['Пройти верификацию']], one_time_keyboard=True)
    )

# Начало процесса верификации
def verification(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id not in unverified_users:
        unverified_users.add(user_id)

    update.message.reply_text(
        "Пожалуйста, отправьте свой контакт для верификации.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Отправить контакт", request_contact=True)]],
            one_time_keyboard=True
        )
    )

    return VERIFY_CONTACT

# Обработка отправки контакта
def contact(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    contact = update.message.contact

    if contact:
        update.message.reply_text("Спасибо! Проверяем вашу верификацию...")
        time.sleep(10)  # Задержка в 10 секунд для проверки (можно заменить на реальную проверку)

        # Успешная верификация
        update.message.reply_text("Верификация прошла успешно! Теперь вы можете писать в чат.")
        
        # Убираем пользователя из списка не верифицированных
        if user_id in unverified_users:
            unverified_users.remove(user_id)

        # Разблокируем пользователя в чате
        context.bot.restrict_chat_member(update.message.chat_id, user_id, can_send_messages=True)

    return ConversationHandler.END

# Завершение верификации
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Верификация отменена.")
    return ConversationHandler.END

def main():
    try:
        # Создание апдейтера и диспетчера
        updater = Updater(BOT_TOKEN)
        dp = updater.dispatcher

        # Обработчик новых участников
        dp.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

        # Обработчик команды /start
        dp.add_handler(CommandHandler("start", start_command))

        # Обработчик сообщений от пользователей
        dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Обработчик для верификации
        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex('^Пройти верификацию$'), verification)],
            states={
                VERIFY_CONTACT: [MessageHandler(filters.CONTACT, contact)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )
        dp.add_handler(conv_handler)

        # Запуск бота
        updater.start_polling()
        updater.idle()

    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
