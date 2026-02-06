import os
from flask import Flask
from flask_cors import CORS
from models import storage_layer
from datetime import timedelta

web_application = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(web_application)

web_application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
if not web_application.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable must be set for production use")
web_application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'sqlite:///../gamified_elearning.db'
)
web_application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
web_application.config['FILE_STORAGE_PATH'] = os.path.join(os.path.dirname(__file__), '../uploads')
web_application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
web_application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

os.makedirs(web_application.config['FILE_STORAGE_PATH'], exist_ok=True)
os.makedirs(os.path.join(web_application.config['FILE_STORAGE_PATH'], 'profiles'), exist_ok=True)
os.makedirs(os.path.join(web_application.config['FILE_STORAGE_PATH'], 'coursework'), exist_ok=True)
os.makedirs(os.path.join(web_application.config['FILE_STORAGE_PATH'], 'submissions'), exist_ok=True)

storage_layer.init_app(web_application)

from routes import *

if __name__ == '__main__':
    with web_application.app_context():
        storage_layer.create_all()
    
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    web_application.run(host='0.0.0.0', port=5000, debug=debug_mode)