from pyrogram import Client, filters
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup
import asyncio

# Укажите только bot_token
bot_token = '8116216134:AAEiir14BK2tYchpAykLkw9shlAnIugqEvo'

# Создаем объект бота
app = Client("my_bot", bot_token=bot_token)

# Для управления пользователями в чате
async def restrict_user(chat_id, user_id):
    # Запрещаем пользователю отправлять сообщения в чат
    await app.restrict_chat_member(chat_id, user_id, can_send_messages=False)

async def unrestrict_user(chat_id, user_id):
    # Разрешаем пользователю отправлять сообщения в чат
    await app.restrict_chat_member(chat_id, user_id, can_send_messages=True)

# Обработка нового сообщения
@app.on_message(filters.chat('@your_channel_username') & filters.text)
async def handle_message(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Если пользователь не прошел верификацию
    await restrict_user(chat_id, user_id)

    # Отправляем сообщение с инструкциями и кнопкой
    verification_button = KeyboardButton("Пройти верификацию")
    reply_markup = ReplyKeyboardMarkup([[verification_button]])

    await message.reply(
        "Для того чтобы иметь возможность писать в чат, необходимо пройти верификацию. Нажмите кнопку ниже.",
        reply_markup=reply_markup
    )

# Обработка команды /start
@app.on_message(filters.command('start'))
async def start(client, message):
    await message.reply("Привет! Для того чтобы пройти верификацию, нажмите кнопку ниже.")

# Обработка кнопки "Пройти верификацию"
@app.on_message(filters.text & filters.regex("Пройти верификацию"))
async def verification(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Отправляем запрос на отправку контакта
    contact_button = KeyboardButton("Отправить мой контакт", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]])

    await message.reply(
        "Пожалуйста, отправьте свой контакт, чтобы пройти верификацию.",
        reply_markup=reply_markup
    )

# Обработка полученного контакта
@app.on_message(filters.contact)
async def contact_received(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Ждем 10 секунд перед подтверждением верификации
    await asyncio.sleep(10)

    # Подтверждаем верификацию и разблокируем пользователя
    await unrestrict_user(chat_id, user_id)
    await message.reply("Верификация прошла успешно! Теперь вы можете писать в чат.")

# Запуск бота
app.run()
