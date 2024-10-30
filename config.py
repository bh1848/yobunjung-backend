import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://yobunjung:1234@localhost/yobunjung_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
