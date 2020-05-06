import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.environ.get("SECRET_KEY")
API_KEY = os.environ.get("API_KEY")
# Enable debug mode.
DEBUG = os.environ.get("DEBUG")

# Connect to the database
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

# Disable track modifications option
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")

UPLOADED_PHOTOS_DEST = os.path.join(basedir, "/static/uploads")

AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN")
API_AUDIENCE = os.environ.get("API_AUDIENCE")
AUTH0_ACCESS_TOKEN_URL = os.environ.get("AUTH0_ACCESS_TOKEN_URL")
AUTH0_AUTHORIZE_URL = os.environ.get("AUTH0_AUTHORIZE_URL")
AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID")
AUTH0_CALLBACK_URL = os.environ.get("AUTH0_CALLBACK_URL")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET")
AUTH0_ALLOWED_CALLBACK = os.environ.get("AUTH0_ALLOWED_CALLBACK")
CONF_URL = os.environ.get("CONF_URL")
