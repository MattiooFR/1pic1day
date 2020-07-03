from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy

# from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_bootstrap import Bootstrap
from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()


# photos = UploadSet("photos", IMAGES)


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

    # configure_uploads(app, photos)
    # patch_request_class(app)  # set maximum file size, default is 16MB

    CORS(app, resources={r"*": {"origins": r"*"}})

    return app


from app import models
