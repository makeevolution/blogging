from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

# permission_required is a decorator.
# Use it like admin_required function below.
# A decorator is like a set-up and teardown thing.
# You can customize it to do something before calling f, something after calling f,
# or any combination.
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)