import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'eval_ai_hackathon_super_secret_key_2026'
    
    # MySQL Primary Connection Credentials
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'answer_eval_db'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    
    # SQLAlchemy URI (Primary MySQL with SQLite Fallback)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    
    # Fallback SQLite DB Path
    SQLITE_DB_PATH = os.path.join(BASE_DIR, 'instance', 'answer_eval.db')
    SQLITE_DATABASE_URI = f"sqlite:///{SQLITE_DB_PATH}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload Directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
    
    # AI Evaluation Weights
    SIMILARITY_WEIGHT = 0.50
    KEYWORD_WEIGHT = 0.35
    GRAMMAR_WEIGHT = 0.15
    
    # Optional Gemini API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or ''
