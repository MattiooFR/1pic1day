from functools import wraps

from flask import jsonify, redirect, render_template, session, url_for
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException

import json

from app import app, auth0


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page here
            return redirect("/")
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def get_greeting():
    return render_template("index.html")


@app.route("/upload")
def upload_images():
    # cloudinary.uploader.upload(
    #     "sample.jpg", crop="limit", tags="samples", width=1024, height=1024)
    return


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=app.config.get("AUTH0_ALLOWED_CALLBACK")
    )


@app.route("/callback")
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get("userinfo")
    userinfo = resp.json()

    # Store the user information in flask session.
    session["jwt_payload"] = userinfo
    session["profile"] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
        "picture": userinfo["picture"],
    }
    return redirect("/dashboard")


@app.route("/dashboard")
@requires_auth
def dashboard():
    return render_template(
        "dashboard.html",
        userinfo=session["profile"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
    )


@app.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": url_for("home", _external=True),
        "client_id": "trbeSG7dcFv0WcfZI4fGicHuy1KWkj85",
    }
    return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))
