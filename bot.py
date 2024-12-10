import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ChatMemberHandler

# Ваш токен бота
BOT_TOKEN = "8116216134:AAEiir14BK2tYchpAykLkw9shlAnIugqEvo"

# ID чата, в который нужно отправлять уведомления
NOTIFY_CHAT_ID = -1002226636763

# Список разрешённых пользователей
ALLOWED_USERS = [6093206594, 1786923925]  # Добавьте сюда ID пользователей, которым разрешено использовать команду

# Функция для получения ID чата
async def send_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"ID этого чата: {chat_id}")

# Функция для отправки уведомлений о начале процесса верификации
async def send_start_verification_notification(context: ContextTypes.DEFAULT_TYPE, chat_username: str):
    try:
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"Началась верификация в чате @{chat_username}."
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для отправки уведомлений о завершении процесса
async def send_notification_to_admin(context: ContextTypes.DEFAULT_TYPE, message: str, chat_username: str, verified_count: int):
    try:
        await context.bot.send_message(
            NOTIFY_CHAT_ID,
            f"{message}\n\n"
            f"Чат: @{chat_username}\n"
            f"Количество успешно верифицированных пользователей: {verified_count}"
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления: {e}")

# Функция для верификации пользователя
async def verify_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка на ID
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("Вы не авторизованы для выполнения этой команды.")
        return
    
    # Отправляем сообщение о верификации
    await update.message.reply_text("Для того чтобы пройти верификацию, нажмите кнопку ниже.")
    # Добавляем кнопку для начала верификации
    reply_markup = {"inline_keyboard": [[{"text": "Пройти верификацию", "callback_data": "verify"}]]}
    await update.message.reply_text("Нажмите кнопку, чтобы пройти верификацию.", reply_markup=reply_markup)

# Функция для обработки нажатия на кнопку верификации
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "verify":
        # Запрос на контакт
        await query.message.reply_text("Отправьте свой контакт для верификации.")
        # Ожидаем получения контакта
        await query.message.reply_text("Отправьте свой номер телефона для верификации.")

# Функция для обработки полученного контакта
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        await update.message.reply_text("Верификация пройдена, теперь вы можете писать в чат!")
        # Разблокируем пользователя
        await update.message.reply_text("Вы можете писать в чат!")
    else:
        await update.message.reply_text("Для верификации нужен контакт.")

# Функция, которая автоматически запускает верификацию при вступлении в чат
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем информацию о новом пользователе
    new_member = update.message.new_chat_members[0]
    
    # Проводим автоматическую верификацию
    await update.message.reply_text(f"Привет, {new_member.first_name}! Для верификации, пожалуйста, отправьте свой контакт.")
    # Можем сразу запросить контакт для верификации
    await update.message.reply_text("Отправьте свой номер телефона для верификации.")

# Основной асинхронный цикл
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("id", send_chat_id))
    application.add_handler(CommandHandler("verify", verify_user))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.Regex('^Пройти верификацию$'), button))
    application.add_handler(ChatMemberHandler(welcome_user, ChatMemberHandler.MY_CHAT_MEMBER))

    # Запуск бота с поллингом
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
