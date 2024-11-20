from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return '¡Hola desde mi web! Puedes interactuar conmigo a través de Telegram.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))