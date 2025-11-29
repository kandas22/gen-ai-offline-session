"""
Database models for authentication system
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Optional for OTP-only auth
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    otps = db.relationship('OTP', backref='user', lazy=True, cascade='all, delete-orphan')
    oauth_tokens = db.relationship('OAuthAccessToken', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class OTP(db.Model):
    """OTP model for email verification"""
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.String(6), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f'<OTP {self.email} - {self.otp_code}>'


class OAuthClient(db.Model):
    """OAuth client model for registered applications"""
    __tablename__ = 'oauth_clients'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(48), unique=True, nullable=False, index=True)
    client_secret = db.Column(db.String(128), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    redirect_uris = db.Column(db.Text, nullable=False)  # JSON array of URIs
    allowed_scopes = db.Column(db.String(255), default='openid profile email')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_redirect_uri(self, redirect_uri):
        """Validate redirect URI"""
        import json
        uris = json.loads(self.redirect_uris)
        return redirect_uri in uris
    
    def check_client_secret(self, secret):
        """Verify client secret"""
        return self.client_secret == secret
    
    def __repr__(self):
        return f'<OAuthClient {self.client_name}>'


class OAuthAuthorizationCode(db.Model):
    """OAuth authorization code model"""
    __tablename__ = 'oauth_authorization_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(128), unique=True, nullable=False, index=True)
    client_id = db.Column(db.String(48), db.ForeignKey('oauth_clients.client_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    redirect_uri = db.Column(db.String(255), nullable=False)
    scope = db.Column(db.String(255), nullable=False)
    code_challenge = db.Column(db.String(128), nullable=True)  # For PKCE
    code_challenge_method = db.Column(db.String(10), nullable=True)  # S256 or plain
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        """Check if authorization code is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f'<AuthCode {self.code[:8]}...>'


class OAuthAccessToken(db.Model):
    """OAuth access token model"""
    __tablename__ = 'oauth_access_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    refresh_token = db.Column(db.String(255), unique=True, nullable=True, index=True)
    client_id = db.Column(db.String(48), db.ForeignKey('oauth_clients.client_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    scope = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    refresh_token_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    revoked = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        """Check if access token is still valid"""
        return not self.revoked and datetime.utcnow() < self.expires_at
    
    def __repr__(self):
        return f'<AccessToken {self.access_token[:8]}...>'
