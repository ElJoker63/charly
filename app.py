import os
from flask import Flask, send_file, abort
import requests
from urllib.parse import unquote

app = Flask(__name__)

# Configuración
UPLOAD_DIR = 'uploads'
BASE_URL = "https://charly-579759777497.herokuapp.com/"

# Ruta principal
@app.route('/')
def index():
    return 'Servidor de archivos activo'

# Ruta para servir archivos
@app.route('/file/<user_id>/<filename>')
def serve_file(user_id, filename):
    try:
        # Decodificar el nombre del archivo por si contiene caracteres especiales
        filename = unquote(filename)
        
        # Construir la URL completa
        full_url = BASE_URL + filename

        # Obtener el archivo de la URL remota
        response = requests.get(full_url)
        
        if response.status_code == 200:
            # Si la respuesta es exitosa, enviar el archivo
            return send_file(
                response.content,
                download_name=filename,
                as_attachment=True
            )
        else:
            # Si no se encuentra el archivo, devolver un error 404
            abort(404, description="Archivo no encontrado")
    except Exception as e:
        return f"Error: {str(e)}", 500

# Ruta para listar archivos de un usuario
@app.route('/files/<user_id>')
def list_files(user_id):
    try:
        user_dir = os.path.join(UPLOAD_DIR, user_id)
        if not os.path.exists(user_dir):
            return "No se encontraron archivos para este usuario", 404
            
        files = os.listdir(user_dir)
        if not files:
            return "El directorio está vacío", 404
            
        file_list = "<h1>Archivos disponibles</h1><ul>"
        for file in files:
            file_path = os.path.join(user_dir, file)
            size = os.path.getsize(file_path)
            file_url = f"/file/{user_id}/{file}"
            file_list += f'<li><a href="{file_url}">{file}</a> ({format_size(size)})</li>'
        file_list += "</ul>"
        
        return file_list
        
    except Exception as e:
        return f"Error: {str(e)}", 500

def format_size(size_bytes):
    """Formatea el tamaño del archivo a una forma legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

if __name__ == '__main__':
    # Asegurarse de que existe el directorio de uploads
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Obtener el puerto de las variables de entorno o usar 5000 por defecto
    port = int(os.environ.get('PORT', 5000))
    
    # Ejecutar la aplicación
    app.run(host='0.0.0.0', port=port)