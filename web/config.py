import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'longcyber')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///uploaded_files.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'logn2') 
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024  # 300MB max file size
    ADMIN_USERS = ['admin', 'administrator']

    # Cuckoo API URL
    CUCKOO_API_URL = os.getenv('CUCKOO_API_URL', 'http://localhost:8000')
    CUCKOO_CREATE_FILE_URL = f'{CUCKOO_API_URL}/apiv2/tasks/create/file'

    # Machine learning model URL
    ML_MODEL_URL = os.getenv('ML_MODEL_URL', 'http://localhost:5001')
    ML_PREDICT_URL = f'{ML_MODEL_URL}/predict'
    ML_ADD_TASK_URL = f'{ML_MODEL_URL}/add_task'

