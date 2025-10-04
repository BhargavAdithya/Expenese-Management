from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from models.user import User

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user = User.query.get(get_jwt_identity())
            if user.role != required_role:
                return jsonify({"error": "Permission denied"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

