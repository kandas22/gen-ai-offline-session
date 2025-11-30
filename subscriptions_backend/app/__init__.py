from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    jwt.init_app(app)
    
    # Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.yaml'  # We'll need to serve this or put it in static
    
    # For now, let's assume we'll serve the yaml from a route or static folder
    # But to make it easy, let's just use the file we'll create in the root and serve it
    
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "Subscription Tracker API"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Register Blueprints (we'll create these later)
    from app.routes import auth, subscriptions, usage, analytics
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(subscriptions.bp, url_prefix='/api/subscriptions')
    app.register_blueprint(usage.bp, url_prefix='/api/usage')
    app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200
        
    @app.route('/static/swagger.yaml')
    def swagger_spec():
        from flask import send_from_directory
        import os
        # Assuming swagger.yaml is in the root of subscriptions_backend
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        return send_from_directory(root_dir, 'swagger.yaml')

    return app
