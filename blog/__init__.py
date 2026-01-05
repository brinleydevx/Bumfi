from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"

def create_app():
    import os

    # create app; use instance folder for the database
    app = Flask(__name__, static_folder="static", instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    login_manager.init_app(app)
    app.config["SECRET_KEY"] = "dev-key"
    # Database configuration
    # Prefer a DATABASE_URL env var (e.g. mysql+pymysql://...), fall back to instance SQLite for local dev
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    else:
        # Use an SQLite DB stored in the instance folder to avoid accidental duplicates
        db_path = os.path.join(app.instance_path, 'blog.db')
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Uploads
    app.config['UPLOAD_FOLDER'] = "blog/static/uploads"
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2 MB limit
    # Mail settings (optional) - configure in production via env vars
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@bumfi.local'

    db.init_app(app)
    migrate.init_app(app, db)

    # Optional TLS/SSL configuration for some DB drivers (e.g. PyMySQL)
    # Provide the path to a CA file via the DB_SSL_CA env var to enable TLS verification.
    ca = os.environ.get('DB_SSL_CA')
    if ca:
        # SQLAlchemy accepts engine options via `SQLALCHEMY_ENGINE_OPTIONS`
        app.config.setdefault('SQLALCHEMY_ENGINE_OPTIONS', {})
        app.config['SQLALCHEMY_ENGINE_OPTIONS']['connect_args'] = {'ssl': {'ca': ca}}

    from .routes import main
    app.register_blueprint(main)
    from blog import routes,models
    return app

@login_manager.user_loader
def load_user(user_id):
    from blog.models import User
    return User.query.get(int(user_id))