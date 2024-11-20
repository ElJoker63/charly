import telebot
import os
import uuid
from telebot import types

TOKEN = '6816962345:AAExMSjcfzv0gHWDEqLMhlfpzLSpfQKZmsU'
HOSTNAME = os.environ.get('HOSTNAME', '')
bot = telebot.TeleBot(token=TOKEN)

# Directorio base para almacenar archivos
UPLOAD_DIR = 'uploads'

@bot.message_handler(content_types=['document'])
def handle_doc(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)  


    # Crear directorio para el usuario si no existe
    user_dir = os.path.join(UPLOAD_DIR, str(message.from_user.id))
    os.makedirs(user_dir, exist_ok=True)

    # Generar un nombre único para el archivo
    file_name = str(uuid.uuid4()) + '_' + message.document.file_name
    file_path = os.path.join(user_dir, file_name)

    with open(file_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Construir la URL para acceder al archivo desde la web
    file_url = f"https://{HOSTNAME}/{str(message.from_user.id)}/{file_name}"
    bot.reply_to(message, f"Archivo guardado. Puedes acceder a él desde: {file_url}")
