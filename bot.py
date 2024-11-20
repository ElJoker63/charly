import os
import telebot
from telebot import types
import re
from datetime import datetime

# Configuración del bot
TOKEN = '6816962345:AAExMSjcfzv0gHWDEqLMhlfpzLSpfQKZmsU'
UPLOAD_DIR = 'files'
HOSTNAME = "https://charly-579759777497.herokuapp.com/"

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
    # Enviar nuevo mensaje en lugar de responder
    bot.send_message(message.chat.id, "¡Hola! Envíame cualquier archivo y lo guardaré para ti.")

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
        #safe_filename = sanitize_filename(original_filename)
        file_path = os.path.join(user_dir, original_filename)
        
        # Guardar archivo
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Crear botón inline
        markup = types.InlineKeyboardMarkup()
        download_button = types.InlineKeyboardButton(
            text="📥 Descargar",
            url=f"{HOSTNAME}file/{message.from_user.id}/{original_filename}"
        )
        markup.add(download_button)
        
        # Enviar mensaje con información detallada y botón
        response_text = (
            f"✅ Archivo guardado exitosamente\n\n"
            f"📄 Nombre: <a href='{HOSTNAME}file/{message.from_user.id}/{original_filename}'>{original_filename}</a>\n"
            f"📁 Tamaño: {format_size(message.document.file_size)}\n"
            #f"📂 Guardado en: {file_path}"
        )
        
        # Enviar nuevo mensaje con botón en lugar de responder
        bot.send_message(
            message.chat.id,
            response_text,
            reply_markup=markup,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error al procesar el archivo: {str(e)}")

@bot.message_handler(commands=['files'])
def list_files(message):
    """Muestra los archivos guardados por el usuario"""
    try:
        user_dir = os.path.join(UPLOAD_DIR, str(message.from_user.id))
        if not os.path.exists(user_dir):
            bot.send_message(message.chat.id, "📂 Aún no has guardado ningún archivo.")
            return
            
        files = os.listdir(user_dir)
        if not files:
            bot.send_message(message.chat.id, "📂 Tu carpeta está vacía.")
            return
            
        # Crear lista de archivos con botones para cada uno
        response = "📂 Tus archivos guardados:\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)
        
        for file in files:
            file_path = os.path.join(user_dir, file)
            size = os.path.getsize(file_path)
            response += f"📄 <a href='{HOSTNAME}file/{message.from_user.id}/{file}'>{file}</a> ({format_size(size)})\n"
            
            # Agregar botón para cada archivo
            button = types.InlineKeyboardButton(
                text=f"📥 Descargar",
                url=f"{HOSTNAME}file/{message.from_user.id}/{file}"
            )
            markup.add(button)
            
        # Enviar mensaje con botones
        bot.send_message(
            message.chat.id,
            response,
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error al listar archivos: {str(e)}")

def main():
    try:
        # Eliminar webhook antes de iniciar el polling
        bot.remove_webhook()
        print("Webhook eliminado")
        
        print("Bot iniciado!")
        # Usar infinity_polling para reconexión automática
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Error al iniciar el bot: {e}")

if __name__ == "__main__":
    main()