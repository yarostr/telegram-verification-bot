import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import time

# Ваш токен
BOT_TOKEN = "8116216134:AAEiir14BK2tYchpAykLkw9shlAnIugqEvo"

# ID чата, в который нужно отправлять уведомления
NOTIFY_CHAT_ID = -1002226636763

# Словарь для хранения состояния верификации пользователей
verified_users = {}

# Список разрешённых пользователей для запуска команд
ALLOWED_USERS = [6093206594, 1786923925]  # Замените на свои ID пользователей

# Функция для запрета пользователю писать
async def restrict_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if user_id not in verified_users or not verified_users[user_id]:
        await update.message.delete()  # Удаляем сообщение
        await update.message.reply_text(
            "Вы должны пройти верификацию, чтобы писать в этот чат. Нажмите кнопку для начала."
        )
        # Отправляем кнопку для верификации
        keyboard = [
            [InlineKeyboardButton("Пройти верификацию", callback_data='verify')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите кнопку, чтобы пройти верификацию:", reply_markup=reply_markup)

# Функция, которая обрабатывает нажатие кнопки
async def start_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    # Отправляем пользователю запрос на отправку контакта
    keyboard = [[InlineKeyboardButton("Отправить контакт", request_contact=True)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Для прохождения верификации отправьте свой контакт.",
        reply_markup=reply_markup
    )

# Функция для обработки контакта пользователя
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    contact = update.message.contact

    # Верификация пользователя (на основании полученного контакта)
    if contact:
        # Можно здесь добавить дополнительные проверки (например, проверку номера телефона)
        verified_users[user_id] = True
        await update.message.reply_text(
            "Верификация прошла успешно! Теперь вы можете писать в чат."
        )
        # Разблокировать пользователя в чате
        await update.effective_chat.restrict_member(user_id, can_send_messages=True)
    else:
        await update.message.reply_text("Для верификации необходимо отправить свой контакт.")

# Функция для ограничения прав пользователя
async def restrict_user_in_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    # Ограничиваем пользователя в чате до прохождения верификации
    if user_id not in verified_users or not verified_users[user_id]:
        await update.effective_chat.restrict_member(user_id, can_send_messages=False)
        await restrict_user(update, context)

# Команда для начала верификации
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in verified_users or not verified_users[user_id]:
        keyboard = [
            [InlineKeyboardButton("Пройти верификацию", callback_data='verify')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Нажмите кнопку для верификации.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Вы уже прошли верификацию!")

# Команда для админов, чтобы отправить уведомление
async def send_notification_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Эта команда отправляет уведомление в чат администратора
    if update.effective_user.id in ALLOWED_USERS:
        message = "Верификация прошла успешно! Пользователь теперь может писать в чат."
        await context.bot.send_message(NOTIFY_CHAT_ID, message)

# Функция для запуска бота
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ChatType.GROUP, restrict_user_in_chat))
    application.add_handler(CommandHandler("notify", send_notification_to_admin))
    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))

    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
