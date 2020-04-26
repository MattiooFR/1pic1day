import cloudinary
import cloudinary.api
import cloudinary.uploader
from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config.from_pyfile("../config.py")
db = SQLAlchemy(app)
migrate = Migrate(app, db)


CORS(app)


cloudinary.config.update = {
    "cloud_name": app.config.get("CLOUDINARY_CLOUD_NAME"),
    "api_key": app.config.get("CLOUDINARY_API_KEY"),
    "api_secret": app.config.get("CLOUDINARY_API_SECRET"),
}

oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=app.config.get("AUTH0_CLIENT_ID"),
    client_secret=app.config.get("AUTH0_CLIENT_SECRET"),
    api_base_url=app.config.get("AUTH0_DOMAIN"),
    access_token_url=app.config.get("AUTH0_ACCESS_TOKEN_URL"),
    authorize_url=app.config.get("AUTH0_AUTHORIZE_URL"),
    client_kwargs={"scope": "openid profile email"},
)

from app import models, routes
