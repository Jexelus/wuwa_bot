# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл requirements.txt в рабочую директорию
COPY req.txt .

# Устанавливаем зависимости из файла requirements.txt
RUN pip install --no-cache-dir -r req.txt
RUN pip install psycopg2-binary

# Копируем остальные файлы в рабочую директорию
COPY . .

# Запускаем приложение
CMD ["python", "bot.py"]