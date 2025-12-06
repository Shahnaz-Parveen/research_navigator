import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Use /tmp for database on Render (writable location)
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.environ.get('DATABASE_URL') or os.path.join('/tmp', 'research_navigator.db')
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
