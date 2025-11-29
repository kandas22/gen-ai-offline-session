"""
Database initialization script
Creates database tables and seeds initial OAuth client for Lovable AI
"""
import secrets
import json
from app import app
from models import db, OAuthClient


def generate_client_credentials():
    """Generate secure client ID and secret"""
    client_id = secrets.token_urlsafe(24)
    client_secret = secrets.token_urlsafe(48)
    return client_id, client_secret


def init_database():
    """Initialize database and create tables"""
    with app.app_context():
        print("\n" + "="*60)
        print("🗄️  Database Initialization")
        print("="*60)
        
        # Create all tables
        print("\n📋 Creating database tables...")
        db.create_all()
        print("✅ Tables created successfully")
        
        # Check if Lovable AI client already exists
        lovable_client = OAuthClient.query.filter_by(client_name='Lovable AI').first()
        
        if lovable_client:
            print("\n⚠️  Lovable AI OAuth client already exists")
            print(f"   Client ID: {lovable_client.client_id}")
            print("   (Client secret is stored securely)")
        else:
            # Create OAuth client for Lovable AI
            print("\n🔑 Creating OAuth client for Lovable AI...")
            
            client_id, client_secret = generate_client_credentials()
            
            # Default redirect URIs for Lovable AI
            redirect_uris = [
                'http://localhost:5001/auth/callback',
                'http://localhost:3000/auth/callback',
                'https://lovable.ai/oauth/callback',
                'https://lovable.dev/oauth/callback'
            ]
            
            lovable_client = OAuthClient(
                client_id=client_id,
                client_secret=client_secret,
                client_name='Lovable AI',
                redirect_uris=json.dumps(redirect_uris),
                allowed_scopes='openid profile email'
            )
            
            db.session.add(lovable_client)
            db.session.commit()
            
            print("✅ OAuth client created successfully")
            print("\n" + "="*60)
            print("📝 LOVABLE AI OAUTH CREDENTIALS")
            print("="*60)
            print(f"\nClient ID:\n{client_id}")
            print(f"\nClient Secret:\n{client_secret}")
            print("\nAuthorized Redirect URIs:")
            for uri in redirect_uris:
                print(f"  - {uri}")
            print("\nAllowed Scopes:")
            print("  - openid")
            print("  - profile")
            print("  - email")
            print("\n" + "="*60)
            print("⚠️  IMPORTANT: Save these credentials securely!")
            print("   You'll need them to configure Lovable AI")
            print("="*60)
        
        # Create a test OAuth client for development
        test_client = OAuthClient.query.filter_by(client_name='Test Client').first()
        
        if not test_client:
            print("\n🧪 Creating test OAuth client...")
            
            test_client_id, test_client_secret = generate_client_credentials()
            
            test_redirect_uris = [
                'http://localhost:3000/callback',
                'http://localhost:8080/callback'
            ]
            
            test_client = OAuthClient(
                client_id=test_client_id,
                client_secret=test_client_secret,
                client_name='Test Client',
                redirect_uris=json.dumps(test_redirect_uris),
                allowed_scopes='openid profile email'
            )
            
            db.session.add(test_client)
            db.session.commit()
            
            print("✅ Test OAuth client created")
            print(f"\nTest Client ID: {test_client_id}")
            print(f"Test Client Secret: {test_client_secret}")
        
        print("\n" + "="*60)
        print("✅ Database initialization complete!")
        print("="*60)
        print("\n📚 Next Steps:")
        print("1. Update your .env file with email settings (if using SMTP)")
        print("2. Add the OAuth credentials to your Lovable AI configuration")
        print("3. Start the server: python app.py")
        print("4. Test authentication: POST /auth/send-otp")
        print("\n")


if __name__ == '__main__':
    init_database()
