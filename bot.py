import logging
from telegram import Update, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ChatMemberHandler
import asyncio

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = '8116216134:AAEiir14BK2tYchpAykLkw9shlAnIugqEvo'

# Массив для хранения информации о верификации пользователей
verified_users = {}

# Функция старта
async def start(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f"User {user.first_name} {user.last_name} ({user.id}) started the bot.")
    # Приветственное сообщение и кнопка для верификации
    keyboard = [[KeyboardButton("Пройти верификацию", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Привет! Чтобы начать верификацию, нажми кнопку ниже и отправь свой контакт.', reply_markup=reply_markup)

# Обработка команды /verify
async def verify(update: Update, context: CallbackContext):
    keyboard = [[KeyboardButton("Пройти верификацию", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Нажмите кнопку ниже для прохождения верификации.', reply_markup=reply_markup)

# Обработка контакта от пользователя
async def handle_contact(update: Update, context: CallbackContext):
    user = update.message.from_user
    contact = update.message.contact

    if contact:
        # Добавляем пользователя в список верифицированных
        verified_users[user.id] = contact.phone_number
        logger.info(f"User {user.first_name} {user.last_name} ({user.id}) verified with phone number {contact.phone_number}")
        await update.message.reply_text('Спасибо за верификацию! Теперь ты можешь писать в чат.')
    else:
        await update.message.reply_text('Ошибка! Попробуй еще раз.')

# Обработка вступления нового пользователя в чат
async def welcome_new_member(update: Update, context: CallbackContext):
    # Проверка на каждого нового члена
    for member in update.message.new_chat_members:
        # Приветственное сообщение
        await update.message.reply_text(f'Привет, {member.full_name}! Чтобы писать в чат, пройди верификацию.')

# Запуск бота
async def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verify", verify))
    application.add_handler(MessageHandler(filters.Contact, handle_contact))
    application.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.MY_CHAT_MEMBER))

    # Запуск бота
    logger.info("Бот запущен.")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
