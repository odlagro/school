# school/auth/utils.py
from functools import wraps
from flask import abort, redirect, url_for, current_app
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def _serializer():
    secret = current_app.config.get("SECRET_KEY")
    return URLSafeTimedSerializer(secret_key=secret, salt="school-auth-reset")


def generate_reset_token(email: str) -> str:
    return _serializer().dumps(email)


def verify_reset_token(token: str, max_age: int = 3600):
    try:
        return _serializer().loads(token, max_age=max_age)
    except SignatureExpired:
        return None
    except BadSignature:
        return None


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
