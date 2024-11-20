# Используем официальный образ Python
FROM python:3.12-slim


RUN apt-get update && \
    apt-get install -y curl build-essential libpq-dev && \
    apt-get clean && \
    apt install python3-dev -y &&\
    apt-get install build-essential -y
# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё содержимое проекта в рабочую директорию контейнера
COPY project .

# Устанавливаем переменные окружения, если нужно
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV PYTHONPATH=/app

# Запускаем ваше приложение
CMD  ["ls"]
