import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from database import init_db
from routes import auth_bp, admin_bp, teacher_bp, student_bp, common_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required runtime folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORT_FOLDER'], exist_ok=True)

    # Initialize Database & Fallback engine
    init_db(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    app.register_blueprint(common_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)

    return app

app = create_app()

if __name__ == '__main__':
    print("[+] Starting Automated Answer Script Evaluation System...")
    print("[+] Application running at: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
