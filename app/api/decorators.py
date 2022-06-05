from functools import wraps
from flask import abort, g

from app.api.errors import forbidden

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions to access this endpoint!")
            return f(*args, **kwargs)
        return decorated_function
    return decorator