from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

# Ваш bot_token
bot_token = '8116216134:AAEiir14BK2tYchpAykLkw9shlAnIugqEvo'

# Создаем объект бота
app = Client("verification_bot", bot_token=bot_token)

# Обработчик новых участников в группе
@app.on_message(filters.new_chat_members)
async def handle_new_member(client, message):
    new_member = message.new_chat_members[0]
    
    # Блокируем пользователя от отправки сообщений
    try:
        await message.chat.restrict_member(new_member.id, can_send_messages=False)
    except Exception as e:
        print(f"Ошибка при ограничении пользователя: {e}")
    
    # Отправляем сообщение о необходимости верификации
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Пройти верификацию", callback_data="start_verification")]
    ])
    
    await message.chat.send_message(
        f"Привет, {new_member.first_name}! Для того чтобы иметь возможность писать в чат, нужно пройти верификацию.",
        reply_markup=keyboard
    )

# Обработчик нажатия на кнопку
@app.on_callback_query(filters.regex("start_verification"))
async def verification_start(client, callback_query):
    # Отправляем сообщение с инструкцией
    await callback_query.answer("Отправьте свой контакт для верификации.")
    
    # Просим отправить контакт
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отправить контакт", request_contact=True)]
    ])
    
    await callback_query.message.edit_text(
        "Нажмите кнопку ниже и отправьте свой контакт для верификации.",
        reply_markup=keyboard
    )

# Обработчик получения контакта
@app.on_message(filters.contact)
async def handle_contact(client, message):
    contact = message.contact

    # Здесь можно проверять контакт, например, на уникальность
    # Например, сохранение в базу данных для предотвращения повторной верификации

    # Ожидаем 10 секунд перед завершением верификации
    await asyncio.sleep(10)

    # Подтверждаем успешную верификацию
    await message.reply(f"Верификация пройдена! Теперь вы можете писать в чат.")

    # Разблокируем пользователя
    try:
        await message.chat.restrict_member(message.from_user.id, can_send_messages=True)
    except Exception as e:
        print(f"Ошибка при разблокировке пользователя: {e}")

# Запуск бота
app.run()
