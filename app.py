import os
from flask import Flask, send_file, abort

app = Flask(__name__)

# Configuración
UPLOAD_DIR = './uploads'

# Ruta principal
@app.route('/')
def index():
    return 'Servidor de archivos activo'

@app.route('/file/<user_id>/<filename>')
def serve_file(user_id, filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, user_id, filename)
        print(f"Checking file existence: {file_path}")
        if os.path.exists(file_path):
            print(file_path)
            return send_file(path_or_file=file_path, download_name=filename)
        else:
            abort(404, description="Archivo no encontrado")
    except Exception as e:
        return f"Error al servir el archivo: {str(e)}", 500
    

@app.route('/files/<user_id>')
def list_files(user_id):
    try:
        user_dir = os.path.join(UPLOAD_DIR, user_id)

        if not os.path.exists(user_dir):
            return "User directory not found", 404

        files = os.listdir(user_dir)

        if not files:
            return "No files found for this user", 404

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