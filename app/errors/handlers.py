from flask import render_template, session
from app import db
from app.errors import bp
import json


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
