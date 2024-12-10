import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ChatMemberHandler, CallbackContext

# Включаем логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Я бот, готов помочь тебе.")

# Обработчик вступления в чат
async def welcome(update: Update, context: CallbackContext) -> None:
    if update.chat_member.new_chat_member.status == "member":
        # Бот приветствует пользователя, когда тот присоединился
        user = update.chat_member.new_chat_member.user
        await update.message.reply_text(f"Привет, {user.first_name}! Добро пожаловать в чат!")

# Главная функция запуска бота
async def main() -> None:
    # Убедитесь, что токен правильный
    application = Application.builder().token('8116216134:AAFSt7xt4Fgb1V63eZzZg0hZjWbUhsJnv1Y').build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.MY_CHAT_MEMBER))

    # Запуск бота
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
