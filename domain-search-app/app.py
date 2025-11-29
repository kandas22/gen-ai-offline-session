"""
Flask Domain Search Application
A web application for searching domain information using WhoisXML API
with email/OTP authentication and OAuth 2.0 support
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from whois_client import WhoisClient
from models import db
from auth_routes import auth_bp
from oauth_routes import oauth_bp
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)
app.config.from_object(Config)

# Try to connect to database with fallback to SQLite
database_url = app.config['SQLALCHEMY_DATABASE_URI']
database_type = 'Supabase PostgreSQL' if 'postgres' in database_url else 'SQLite'

try:
    # Test the connection before initializing
    if 'postgres' in database_url:
        print(f"\n🔗 Attempting to connect to {database_type}...")
        test_engine = create_engine(database_url)
        with test_engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print(f"✅ {database_type} connection successful")
        test_engine.dispose()
except Exception as e:
    print(f"\n⚠️  {database_type} connection failed: {str(e)[:100]}")
    print("🔄 Falling back to SQLite...")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth.db'
    database_type = 'SQLite'
    print("✅ Using SQLite database")
    print("💡 To use Supabase, update DATABASE_URL in .env with correct credentials\n")

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[Config.RATELIMIT_DEFAULT],
    storage_uri=Config.RATELIMIT_STORAGE_URL
)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(oauth_bp)

# Initialize WhoisXML client
whois_client = WhoisClient()

# Create database tables
with app.app_context():
    db.create_all()
    print(f"✅ Database tables created in {database_type}")


@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """
    Handle domain search requests
    
    Returns:
        JSON response with domain information or error message
    """
    try:
        # Get domain from request
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        # Validate domain input
        if not domain:
            return jsonify({
                'success': False,
                'message': 'Please enter a domain name'
            }), 400
        
        # Search for domain information
        result = whois_client.search_domain(domain)
        
        # Return result
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 200  # Return 200 even for "not found" to display message
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'An error occurred while processing your request'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    api_configured = Config.validate_api_key()
    return jsonify({
        'status': 'healthy',
        'api_configured': api_configured
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 Flask Domain Search Application")
    print("="*60)
    
    if Config.validate_api_key():
        print("✅ WhoisXML API key configured")
    else:
        print("⚠️  WhoisXML API key not configured")
        print("   Please add your API key to .env file")
        print("   Copy .env.example to .env and add your key")
    
    print("\n🚀 Starting server at http://localhost:5001")
    print("="*60 + "\n")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5001)
