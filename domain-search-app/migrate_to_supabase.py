"""
Migration script to set up Supabase database
Creates all tables in Supabase PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from models import db, User, OTP, OAuthClient, OAuthAuthorizationCode, OAuthAccessToken

# Load environment variables
load_dotenv()

# Get Supabase database URL
SUPABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:CqArIPiNBIHwuuYV@db.ieyumjrmncihgcyhwdpo.supabase.co:5432/postgres')

def migrate_to_supabase():
    """Migrate database to Supabase"""
    print("\n" + "="*60)
    print("🚀 Supabase Database Migration")
    print("="*60)
    
    try:
        # Create engine for Supabase
        print(f"\n📡 Connecting to Supabase...")
        engine = create_engine(SUPABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
        
        # Import app to get the configured db instance
        from app import app
        
        with app.app_context():
            print("\n📋 Creating database tables...")
            
            # Drop existing tables (optional - comment out if you want to keep data)
            # db.drop_all()
            # print("🗑️  Dropped existing tables")
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully")
            
            # List created tables
            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            print(f"\n📊 Created tables ({len(tables)}):")
            for table in tables:
                print(f"   - {table}")
            
            # Check if OAuth client exists
            from models import OAuthClient
            import json
            import secrets
            
            lovable_client = OAuthClient.query.filter_by(client_name='Lovable AI').first()
            
            if not lovable_client:
                print("\n🔑 Creating OAuth client for Lovable AI...")
                
                client_id = secrets.token_urlsafe(24)
                client_secret = secrets.token_urlsafe(48)
                
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
                
                print("✅ OAuth client created")
                print("\n" + "="*60)
                print("📝 LOVABLE AI OAUTH CREDENTIALS")
                print("="*60)
                print(f"\nClient ID:\n{client_id}")
                print(f"\nClient Secret:\n{client_secret}")
                print("\nAuthorized Redirect URIs:")
                for uri in redirect_uris:
                    print(f"  - {uri}")
                print("\n" + "="*60)
            else:
                print("\n✅ OAuth client already exists")
                print(f"   Client ID: {lovable_client.client_id}")
        
        print("\n" + "="*60)
        print("✅ Supabase migration complete!")
        print("="*60)
        print("\n📚 Next Steps:")
        print("1. Your data is now stored in Supabase PostgreSQL")
        print("2. Restart your Flask application")
        print("3. Test authentication endpoints")
        print("4. All user profiles will be stored in Supabase")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in .env file")
        print("2. Ensure Supabase project is active")
        print("3. Verify database credentials")
        print("4. Check network connectivity")
        raise


if __name__ == '__main__':
    migrate_to_supabase()
