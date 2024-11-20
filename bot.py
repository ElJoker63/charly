import os
import telebot
from telebot import types
import re
from datetime import datetime

# Configuración del bot
TOKEN = '6816962345:AAExMSjcfzv0gHWDEqLMhlfpzLSpfQKZmsU'
UPLOAD_DIR = 'uploads'

# Inicializar bot
bot = telebot.TeleBot(TOKEN)

# Asegurar que el directorio de uploads existe
os.makedirs(UPLOAD_DIR, exist_ok=True)

def sanitize_filename(filename):
    """
    Limpia el nombre del archivo de caracteres no deseados y agrega timestamp si ya existe
    """
    # Eliminar caracteres no deseados
    clean_name = re.sub(r'[^\w\-_. ]', '', filename)
    # Separar nombre y extensión
    name, ext = os.path.splitext(clean_name)
    # Agregar timestamp si el archivo ya existe
    return f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

def format_size(size_bytes):
    """
    Formatea el tamaño del archivo a una forma legible
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Envíame cualquier archivo y lo guardaré para ti.")

@bot.message_handler(content_types=['document'])
def handle_doc(message):
    try:
        # Obtener información del archivo
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Crear directorio para el usuario
        user_dir = os.path.join(UPLOAD_DIR, str(message.from_user.id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Obtener y sanitizar el nombre original del archivo
        original_filename = message.document.file_name
        safe_filename = sanitize_filename(original_filename)
        file_path = os.path.join(user_dir, safe_filename)
        
        # Guardar archivo
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Enviar respuesta con información detallada
        response_text = (
            f"✅ Archivo guardado exitosamente\n"
            f"📄 Nombre: {original_filename}\n"
            f"📁 Tamaño: {format_size(message.document.file_size)}\n"
            f"📂 Guardado en: {file_path}"
        )
        bot.reply_to(message, response_text)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error al procesar el archivo: {str(e)}")

@bot.message_handler(commands=['files'])
def list_files(message):
    """Muestra los archivos guardados por el usuario"""
    try:
        user_dir = os.path.join(UPLOAD_DIR, str(message.from_user.id))
        if not os.path.exists(user_dir):
            bot.reply_to(message, "📂 Aún no has guardado ningún archivo.")
            return
            
        files = os.listdir(user_dir)
        if not files:
            bot.reply_to(message, "📂 Tu carpeta está vacía.")
            return
            
        response = "📂 Tus archivos guardados:\n\n"
        for i, file in enumerate(files, 1):
            file_path = os.path.join(user_dir, file)
            size = os.path.getsize(file_path)
            response += f"{i}. 📄 {file} ({format_size(size)})\n"
            
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, f"❌ Error al listar archivos: {str(e)}")

print("Bot iniciado!")
bot.infinity_polling()