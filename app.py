import os
from flask import Flask, send_file, abort, request

app = Flask(__name__)

# Configuración
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

# Ruta principal
@app.route('/')
def index():
    ruta_actual = os.getcwd()
    lists = os.listdir(ruta_actual)
    return lists

@app.route('/file/<user_id>/<filename>')
def serve_file(user_id, filename):
    try:
        file_path = os.path.join(UPLOAD_DIR, user_id, filename)
        app.logger.info(f"Attempting to serve file: {file_path}")
        
        if os.path.exists(file_path):
            app.logger.info(f"File found: {file_path}")
            return send_file(path_or_file=file_path, download_name=filename, as_attachment=True)
        else:
            app.logger.error(f"File not found: {file_path}")
            abort(404, description="Archivo no encontrado")
    except Exception as e:
        app.logger.error(f"Error serving file: {str(e)}")
        return f"Error al servir el archivo: {str(e)}", 500

@app.route('/files/<user_id>')
def list_files(user_id):
    try:
        user_dir = os.path.join(UPLOAD_DIR, user_id)
        app.logger.info(f"Listing files in directory: {user_dir}")

        if not os.path.exists(user_dir):
            app.logger.warning(f"User directory not found: {user_dir}")
            return "User directory not found", 404

        files = os.listdir(user_dir)

        if not files:
            app.logger.info(f"No files found for user: {user_id}")
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
        app.logger.error(f"Error listing files: {str(e)}")
        return f"Error: {str(e)}", 500
    
@app.route('/upload/<user_id>', methods=['POST'])
def upload_file(user_id):
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    if file.filename == '':
        return 'No file selected for uploading', 400
    if file:
        filename = file.filename
        user_dir = os.path.join(UPLOAD_DIR, user_id)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, filename)
        file.save(file_path)
        return 'File successfully uploaded', 201

def format_size(size_bytes):
    """Formatea el tamaño del archivo a una forma legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

if __name__ == '__main__':
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.logger.setLevel('INFO')
    app.run(host='0.0.0.0', port=port)