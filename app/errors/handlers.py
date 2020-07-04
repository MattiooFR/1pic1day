from flask import render_template, session
from app import db
from app.errors import bp
import json


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


@bp.errorhandler(AuthError)
def auth_error(e):
    print(AuthError)
    if "profile" in session:
        return render_template(
            "errors/auth_error.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
            auth_error=e.status_code,
        )
    else:
        return render_template(
            "errors/auth_error.html", logged_in=False, auth_error=e.status_code
        )


@bp.app_errorhandler(401)
def unauthorized(error):
    if "profile" in session:
        return render_template(
            "errors/401.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
        )
    else:
        return render_template("errors/401.html", logged_in=False)


@bp.app_errorhandler(404)
def not_found(error):
    if "profile" in session:
        return render_template(
            "errors/404.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
        )
    else:
        return render_template("errors/404.html", logged_in=False)


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if "profile" in session:
        return render_template(
            "errors/500.html",
            userinfo=session["profile"],
            userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
            logged_in=True,
        )
    else:
        return render_template("errors/500.html", logged_in=False)
