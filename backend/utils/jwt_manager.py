from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def get_current_user():
    """
    Get current user from JWT token
    
    Returns:
        User object or None
    """
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(user_id)
        return None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None


def jwt_required_with_user(fn):
    """
    Decorator that requires JWT and injects current user
    
    Usage:
        @jwt_required_with_user
        def my_route(current_user):
            # current_user is automatically injected
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        return fn(current_user=current_user, *args, **kwargs)
    
    return wrapper


def optional_jwt_with_user(fn):
    """
    Decorator that optionally checks JWT and injects current user
    Route will work with or without authentication
    
    Usage:
        @optional_jwt_with_user
        def my_route(current_user):
            # current_user will be None if not authenticated
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            current_user = User.query.get(user_id) if user_id else None
        except:
            current_user = None
        
        return fn(current_user=current_user, *args, **kwargs)
    
    return wrapper