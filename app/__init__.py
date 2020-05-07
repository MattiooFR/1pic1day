import os
import time
import hashlib

from authlib.integrations.flask_client import OAuth
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class

app = Flask(__name__)

app.config.from_pyfile("../config.py")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

photos = UploadSet("photos", IMAGES)

configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB

CORS(app, resources={r"*": {"origins": r"*"}})

oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    server_metadata_url=app.config.get("CONF_URL"),
    client_kwargs={"scope": "openid profile email"},
)

from app import models, routes, forms
