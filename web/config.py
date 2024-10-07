import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'longcyber')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///uploaded_files.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'logn2') 
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 300 * 1024 * 1024  # 300MB max file size