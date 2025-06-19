import os
from datetime import datetime, timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret_dev_key')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/nlp_rec'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)