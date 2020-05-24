from functools import wraps
import os
import json

from flask import (
    jsonify,
    redirect,
    render_template,
    session,
    url_for,
    abort,
    flash,
    request,
    current_app,
)
from six.moves.urllib.parse import urlencode
from werkzeug.utils import secure_filename
from jose import jwt
from urllib.request import urlopen

import random
import shutil

import datetime
import time
import hashlib
import sys

from app.models import Album, Image
from app.main.forms import CreateAlbumForm, EditAlbumNameForm
from app import db, photos
from app.main import bp

ALGORITHMS = ["RS256"]


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected.",
            },
            401,
        )

    parts = auth.split()
    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": 'Authorization header must start with "Bearer".',
            },
            401,
        )

    elif len(parts) == 1:
        raise AuthError(
            {"code": "invalid_header", "description": "Token not found."}, 401
        )

    elif len(parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be bearer token.",
            },
            401,
        )

    token = parts[1]
    return token


def check_permissions(permission, payload):
    if "permissions" not in payload:
        raise AuthError(
            {
                "code": "invalid_claims",
                "description": "Permissions not included in JWT.",
            },
            400,
        )

    if permission not in payload["permissions"]:
        raise AuthError(
            {"code": "unauthorized", "description": "Permission not found."}, 403
        )
    return True


def verify_decode_jwt(token):
    jsonurl = urlopen(
        f"https://{current_app.config.get('AUTH0_DOMAIN')}/.well-known/jwks.json"
    )
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if "kid" not in unverified_header:
        raise AuthError(
            {"code": "invalid_header", "description": "Authorization malformed."}, 401
        )

    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=current_app.config.get("API_AUDIENCE"),
                issuer="https://" + current_app.config.get("AUTH0_DOMAIN") + "/",
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError(
                {"code": "token_expired", "description": "Token expired."}, 401
            )

        except jwt.JWTClaimsError:
            raise AuthError(
                {
                    "code": "invalid_claims",
                    "description": "Incorrect claims. Please, check the audience and issuer.",
                },
                401,
            )
        except Exception:
            raise AuthError(
                {
                    "code": "invalid_header",
                    "description": "Unable to parse authentication token.",
                },
                400,
            )
    raise AuthError(
        {
            "code": "invalid_header",
            "description": "Unable to find the appropriate key.",
        },
        400,
    )


def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = session["jwt_payload"]["access_token"]
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except:
                abort(401)

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator


@bp.route("/")
def home():
    if "profile" in session:
        return render_template(
            "index.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
        )
    else:
        return render_template("index.html", logged_in=False)


@bp.route("/auth")
def auth():
    # Handles response from token endpoint
    token = current_app.auth0.authorize_access_token()
    userinfo = current_app.auth0.parse_id_token(token)

    # Store the user information in flask session.
    session["jwt_payload"] = token
    session["profile"] = {
        "user_id": userinfo["sub"],
        "name": userinfo["name"],
        "picture": userinfo["picture"],
    }

    return redirect(url_for("main.home"))


@bp.route("/login")
def login():
    redirect_uri = current_app.config.get("AUTH0_ALLOWED_CALLBACK")
    return current_app.auth0.authorize_redirect(
        redirect_uri, audience=current_app.config.get("API_AUDIENCE")
    )


@bp.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {
        "returnTo": url_for("main.home", _external=True),
        "client_id": "trbeSG7dcFv0WcfZI4fGicHuy1KWkj85",
    }
    return redirect(
        "https://"
        + current_app.config.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(params)
    )


@bp.route("/profile")
@requires_auth("get:albums")
def profile(payload):
    return render_template("profile.html")


@bp.route("/edit")
def edit_album():
    return render_template("index.html")


@bp.route("/albums")
def get_albums():
    return render_template("index.html")


@bp.route("/<album_id>", methods=["GET"])
def get_album(album_id):
    album = Album.query.filter(Album.url == album_id).first()
    if not album:
        flash("Wrong album URL")
        abort(404)

    if len(album.images.filter(Image.viewed == False).all()) == 0:
        for image in album.images.all():
            image.viewed = False
        db.session.commit()

    if (datetime.datetime.now() - album.last_time_viewed) > datetime.timedelta(
        minutes=1
    ) or album.last_photo_viewed is None:
        files_list = [i.url for i in album.images.filter(Image.viewed == False).all()]
        photo_picked = random.choice(files_list)
        album.last_photo_viewed = photo_picked
        album.last_time_viewed = datetime.datetime.now()
        image = Image.query.filter(Image.url == photo_picked).first()
        image.viewed = True

        db.session.commit()
    else:
        photo_picked = album.last_photo_viewed

    if "profile" in session and album.user_id == session["profile"].get("user_id"):
        userinfo = session["profile"]
        can_manage = True
        logged_in = True
    else:
        userinfo = None
        can_manage = False
        logged_in = False

    return render_template(
        "album.html",
        photo=url_for("static", filename="uploads/" + album_id + "/" + photo_picked),
        userinfo=userinfo,
        can_manage=can_manage,
        logged_in=logged_in,
        album_title=album.name,
    )


@bp.route("/create", methods=["GET", "POST"])
def create_album():
    form_album = CreateAlbumForm()
    error = False

    if "profile" in session:
        user_id = session["profile"].get("user_id")
        userinfo = session["profile"]
        logged_in = True
    else:
        user_id = "ANON"
        userinfo = None
        logged_in = False

    if request.method == "GET":
        return render_template(
            "create_album.html",
            form=form_album,
            success=False,
            logged_in=logged_in,
            userinfo=userinfo,
        )
    elif form_album.validate_on_submit():
        form_values = request.form

        album_name = hashlib.md5(
            "unicorn".encode("utf-8") + str(time.time()).encode("utf-8")
        ).hexdigest()[:10]

        try:
            album = Album(name=form_values.get("name"), url=album_name, user_id=user_id)
            db.session.add(album)
            db.session.flush()
            for filename in request.files.getlist(form_album.photo.name):
                name = hashlib.md5(
                    "admin".encode("utf-8") + str(time.time()).encode("utf-8")
                ).hexdigest()[:10]
                photos.save(filename, folder=album_name, name=name + ".")

                file_name = secure_filename(filename.filename)
                file_name = name + "." + file_name.split(".")[-1]

                image = Image(url=file_name, album_id=album.id)
                db.session.add(image)

            db.session.commit()

            success = True

            # if error we rollback the commit
        except BaseException:
            error = True
            db.session.rollback()
            print(sys.exc_info())
            shutil.rmtree(
                os.path.join(current_app.config.get("UPLOADED_PHOTOS_DEST"), album_name)
            )
        finally:
            db.session.close()

            # we flash an error if the creation of an Album didn't work
            if error:
                flash("An error occurred. Try again")
                success = False
            else:
                flash(
                    "The album was created. Accessible at this address : {}".format(
                        "http://localhost:5000/" + album_name
                    )
                )
    else:
        print("error")
        success = False

    return render_template(
        "create_album.html",
        form=form_album,
        success=success,
        logged_in=logged_in,
        userinfo=userinfo,
    )


@requires_auth("patch:album")
@bp.route("/<album_id>/edit", methods=["GET", "POST"])
def edit_album_name(album_id):
    album = Album.query.filter(Album.url == album_id).first()
    if not album:
        flash("Wrong album URL")
        abort(404)
    if request.method == "GET":
        form = EditAlbumNameForm()
        form.name.data = album.name
        return render_template(
            "edit_album.html",
            form=form,
            success=False,
            logged_in=True,
            userinfo=session["profile"],
        )
    else:
        form = EditAlbumNameForm(request.form)
        if form.validate_on_submit():
            form_values = request.form
            album.name = form_values.get("name")
            album.update()
            flash("Album name changed with success!")
            return redirect(url_for("main.get_album", album_id=album.url))


@requires_auth("delete:album")
@bp.route("/<album_id>/delete")
def delete_album(album_id):
    if "profile" in session:
        album = Album.query.filter(Album.url == album_id).first()
        if not album:
            flash("Wrong album URL")
            abort(404)
        elif album.user_id != session["profile"].get("user_id"):
            flash("You are not the owner of this album")
            abort(401)
    return render_template("album.html", files_list=files_list)


# @bp.route("/<album_id>/manage")
# def manage_album(album_id):
#     files_list = os.listdir(current_app.config["UPLOADED_PHOTOS_DEST"])
#     return render_template("album.html", files_list=files_list)


# @bp.route("/delete/<filename>")
# def delete_file(filename):
#     file_path = photos.path(filename)
#     os.remove(file_path)
#     return redirect(url_for("main.manage_file"))


## Error Handling
@bp.errorhandler(AuthError)
def auth_error(e):
    print(AuthError)
    return (
        jsonify({"success": False, "error": e.status_code, "message": e.description}),
        e.status_code,
    )


@bp.errorhandler(400)
def bad_request(error):
    return (jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400)


@bp.errorhandler(405)
def not_allowed(error):
    return (
        jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
        405,
    )


@bp.errorhandler(422)
def unprocessable(error):
    return (jsonify({"success": False, "error": 422, "message": "Unprocessable"}), 422)


@bp.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify({"success": False, "error": 500, "message": "Internal Server Error"}),
        500,
    )
