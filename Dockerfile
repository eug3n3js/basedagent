# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# # Создаем пользователя для безопасности
# RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
# USER app

# # Открываем порт
# EXPOSE 8000
ENV PYTHONUNBUFFERED=1
# Команда по умолчанию
CMD ["python", "src/main/main.py"]
