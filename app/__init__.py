from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy

from flask_bootstrap import Bootstrap

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    oauth.init_app(app)

    app.auth0 = oauth.register(
        "auth0",
        server_metadata_url="https://1pic1day.eu.auth0.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    CORS(app, resources={r"*": {"origins": r"*"}})

    return app


from app import models
