from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize CORS with configuration
    CORS(app, 
         origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000', 'http://localhost:5173']),
         supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True))
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
    
    # Register blueprints with error handling
    try:
        from routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp, url_prefix="/api/auth")
    except ImportError as e:
        print(f"Warning: Could not import auth_routes: {e}")
    
    try:
        from routes.expense_routes import expense_bp
        app.register_blueprint(expense_bp, url_prefix="/api/expenses")
    except ImportError as e:
        print(f"Warning: Could not import expense_routes: {e}")
    
    try:
        from routes.approval_routes import approval_bp
        app.register_blueprint(approval_bp, url_prefix="/api/approvals")
    except ImportError as e:
        print(f"Warning: Could not import approval_routes: {e}")
    
    try:
        from routes.rule_routes import rule_bp
        app.register_blueprint(rule_bp, url_prefix="/api/rules")
    except ImportError as e:
        print(f"Warning: Could not import rule_routes: {e}")
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Expense Management API is running',
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Welcome to Expense Management API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'expenses': '/api/expenses',
                'approvals': '/api/approvals',
                'rules': '/api/rules',
                'health': '/health'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not found',
            'message': 'The requested resource was not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_expired',
            'message': 'The token has expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'invalid_token',
            'message': 'Signature verification failed'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'authorization_required',
            'message': 'Request does not contain an access token'
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'token_revoked',
            'message': 'The token has been revoked'
        }), 401
    
    return app


if __name__ == "__main__":
    app = create_app()
    
    # Create all database tables
    with app.app_context():
        try:
            db.create_all()
            print("=" * 50)
            print("✓ Database tables created successfully!")
            print(f"✓ Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
            print(f"✓ Environment: {os.getenv('FLASK_ENV', 'development')}")
            print(f"✓ Debug Mode: {app.config.get('DEBUG', False)}")
            print(f"✓ Running on: http://localhost:{os.getenv('PORT', 5000)}")
            print("=" * 50)
        except Exception as e:
            print("=" * 50)
            print(f"✗ Error creating database tables: {e}")
            print("=" * 50)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )