from functools import wraps

from flask import jsonify, redirect, render_template, session, url_for, abort, flash
from six.moves.urllib.parse import urlencode
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from app.models import User
from app import db

import json

from app import app, auth0

AUTH0_DOMAIN = app.config.get("AUTH0_DOMAIN")
ALGORITHMS = ["RS256"]
API_AUDIENCE = app.config.get("API_AUDIENCE")


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    print(request.headers)
    auth = request.headers.get("Authorization", None)
    print("heheheee")
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
    jsonurl = urlopen(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    print(unverified_header)
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
                audience=API_AUDIENCE,
                issuer="https://" + AUTH0_DOMAIN + "/",
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


# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         if "profile" not in session:
#             # Redirect to Login page here
#             return redirect("/login")
#         return f(*args, **kwargs)

#     return decorated
def requires_auth(permission=""):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                print(token)
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except:
                abort(401)

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator


@app.route("/")
def home():
    print(session)
    if "profile" in session:
        return render_template(
            "index.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
        )
    else:
        return render_template("index.html", logged_in=False)


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=app.config.get("AUTH0_ALLOWED_CALLBACK"), audience=API_AUDIENCE
    )


@app.route("/profile")
@requires_auth("get:albums")
def profile():
    return render_template("profile.html")


@app.route("/callback")
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()

    resp = auth0.get("userinfo")
    userinfo = resp.json()

    print(userinfo)

    user = User.query.filter(User.email == userinfo["email"]).first()
    error = False

    try:
        if user == None:
            user = User(
                userinfo["name"],
                userinfo["email"],
                userinfo["sub"],
                userinfo["picture"],
            )
            user.insert()

    # if error we rollback the commit
    except BaseException:
        print("error")
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        if error:
            flash("An error occurred. Could not login !")
            return redirect(url_for("home"))
        else:
            flash("Hello " + user.name.split(" ")[0])

        # Store the user information in flask session.
        session["jwt_payload"] = userinfo
        session["profile"] = {
            "user_id": userinfo["sub"],
            "name": userinfo["name"],
            "picture": userinfo["picture"],
        }

        return redirect(url_for("home"))


@app.route("/edit")
def edit_album():
    return render_template("index.html")


@app.route("/albums")
def get_albums():
    return render_template("index.html")


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


@app.route("/create", methods=["GET", "POST"])
def create_album():
    form_album = CreateAlbumForm()
    form_upload = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist("photo"):
            name = hashlib.md5("admin" + str(time.time())).hexdigest()[:15]
            photos.save(filename, name=name + ".")
        success = True
    else:
        success = False
    return render_template("index.html", form=form, success=success)


@app.route("/manage")
def manage_file():
    files_list = os.listdir(app.config["UPLOADED_PHOTOS_DEST"])
    return render_template("manage.html", files_list=files_list)


@app.route("/open/<filename>")
def open_file(filename):
    file_url = photos.url(filename)
    return render_template("index.html", file_url=file_url)


@app.route("/delete/<filename>")
def delete_file(filename):
    file_path = photos.path(filename)
    os.remove(file_path)
    return redirect(url_for("manage_file"))


## Error Handling
@app.errorhandler(AuthError)
def auth_error(e):
    print(AuthError)
    return (
        jsonify({"success": False, "error": e.status_code, "message": e.description}),
        e.status_code,
    )


@app.errorhandler(400)
def bad_request(error):
    return (jsonify({"success": False, "error": 400, "message": "Bad Request"}), 400)


@app.errorhandler(401)
def unauthorized(error):
    return (jsonify({"success": False, "error": 401, "message": "Unauthorized"}), 401)


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"success": False, "error": 404, "message": "Resources Not Found"}),
        404,
    )


@app.errorhandler(405)
def not_allowed(error):
    return (
        jsonify({"success": False, "error": 405, "message": "Method Not Allowed"}),
        405,
    )


@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({"success": False, "error": 422, "message": "Unprocessable"}), 422)


@app.errorhandler(500)
def internal_server_error(error):
    return (
        jsonify({"success": False, "error": 500, "message": "Internal Server Error"}),
        500,
    )
