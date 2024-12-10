# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в рабочую директорию
COPY . .

# Устанавливаем команду по умолчанию для запуска приложения
CMD ["python", "bot.py"]
