import os
from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
from .views.account import account
from .views.main import main, login_manager, mail
from .models import db, bcrypt

load_dotenv()


def create_app():
    # App context
    app = Flask(__name__)

    # App configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{}:{}@{}:{}/{}".format(
        os.environ.get("DATABASE_USERNAME"),
        os.environ.get("DATABASE_PASSWORD"),
        os.environ.get("DATABASE_HOST"),
        os.environ.get("DATABASE_PORT"),
        os.environ.get("DATABASE_NAME"),
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    app.config["MAIL_SERVER"] = os.environ.get("EMAIL_SERVER")
    app.config["MAIL_PORT"] = os.environ.get("EMAIL_PORT")
    app.config["MAIL_USE_SSL"] = os.environ.get("EMAIL_USE_SSL")
    app.config["MAIL_USERNAME"] = os.environ.get("HOST_USER")
    app.config["MAIL_PASSWORD"] = os.environ.get("HOST_PASSWORD")

    # Flask mail
    mail.init_app(app)

    # Flask login
    login_manager.init_app(app)

    # Flask bcrypt
    bcrypt.init_app(app)

    # Flask  sqlalchemy and migrate
    db.init_app(app)
    Migrate(app, db)

    # Registration of views blueprints
    app.register_blueprint(main, url_prefix="/")
    app.register_blueprint(account, url_prefix="/account")

    return app
