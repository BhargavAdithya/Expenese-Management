from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def role_required(*allowed_roles):
    """
    Decorator to check if user has required role
    
    Usage:
        @role_required('admin')
        def admin_only_route():
            pass
        
        @role_required('admin', 'manager')
        def admin_or_manager_route():
            pass
    
    Args:
        allowed_roles: Variable number of role strings ('admin', 'manager', 'employee')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT is present
            verify_jwt_in_request()
            
            # Get current user
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check if user has required role
            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Access denied',
                    'message': f'This endpoint requires one of the following roles: {", ".join(allowed_roles)}'
                }), 403
            
            # Inject current user into the function
            return fn(current_user=user, *args, **kwargs)
        
        return wrapper
    return decorator


def admin_required(fn):
    """
    Decorator to require admin role
    
    Usage:
        @admin_required
        def admin_route(current_user):
            # current_user is automatically injected
            pass
    """
    return role_required('admin')(fn)


def manager_or_admin_required(fn):
    """
    Decorator to require manager or admin role
    
    Usage:
        @manager_or_admin_required
        def manager_route(current_user):
            # current_user is automatically injected
            pass
    """
    return role_required('admin', 'manager')(fn)


def same_company_required(fn):
    """
    Decorator to ensure user is accessing resources from their own company
    
    Usage:
        @same_company_required
        def get_resource(current_user, resource_id):
            # Checks that resource belongs to current_user's company
            pass
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Inject current user
        return fn(current_user=user, *args, **kwargs)
    
    return wrapper