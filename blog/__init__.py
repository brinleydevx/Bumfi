from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    login_manager.init_app(app)
    app.config["SECRET_KEY"] = "dev-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///blog.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    from blog import routes,models
    return app

@login_manager.user_loader
def load_user(user_id):
    from blog.models import User
    return User.query.get(int(user_id))