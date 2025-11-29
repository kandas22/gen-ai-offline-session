"""
Authentication service for OTP and JWT token management
"""
import secrets
import string
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token
from models import db, User, OTP


class AuthService:
    """Service class for authentication operations"""
    
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    OTP_MAX_ATTEMPTS = 5
    
    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        return ''.join(secrets.choice(string.digits) for _ in range(AuthService.OTP_LENGTH))
    
    @staticmethod
    def create_or_get_user(email):
        """Create a new user or get existing user by email"""
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()
        return user
    
    @staticmethod
    def send_otp(email):
        """
        Generate and store OTP for email
        Returns: (success, message, otp_code)
        """
        # Get or create user
        user = AuthService.create_or_get_user(email)
        
        # Check rate limiting - max 5 OTPs per hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_otps = OTP.query.filter(
            OTP.user_id == user.id,
            OTP.created_at > one_hour_ago
        ).count()
        
        if recent_otps >= AuthService.OTP_MAX_ATTEMPTS:
            return False, 'Too many OTP requests. Please try again later.', None
        
        # Invalidate previous unused OTPs
        OTP.query.filter_by(user_id=user.id, is_used=False).update({'is_used': True})
        
        # Generate new OTP
        otp_code = AuthService.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=AuthService.OTP_EXPIRY_MINUTES)
        
        otp = OTP(
            user_id=user.id,
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.session.add(otp)
        db.session.commit()
        
        return True, 'OTP sent successfully', otp_code
    
    @staticmethod
    def verify_otp(email, otp_code):
        """
        Verify OTP code for email
        Returns: (success, message, user)
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            return False, 'Invalid email or OTP', None
        
        # Find the most recent unused OTP
        otp = OTP.query.filter_by(
            user_id=user.id,
            otp_code=otp_code,
            is_used=False
        ).order_by(OTP.created_at.desc()).first()
        
        if not otp:
            return False, 'Invalid or expired OTP', None
        
        if not otp.is_valid():
            return False, 'OTP has expired', None
        
        # Mark OTP as used
        otp.is_used = True
        
        # Mark user as verified and update last login
        user.is_verified = True
        user.last_login = datetime.utcnow()
        
        db.session.commit()
        
        return True, 'OTP verified successfully', user
    
    @staticmethod
    def generate_tokens(user):
        """
        Generate JWT access and refresh tokens for user
        Returns: (access_token, refresh_token)
        """
        # Use user ID as identity (Flask-JWT-Extended requires string or int)
        identity = str(user.id)
        
        # Add custom claims for user data
        additional_claims = {
            'email': user.email,
            'is_verified': user.is_verified
        }
        
        access_token = create_access_token(
            identity=identity,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims=additional_claims,
            expires_delta=timedelta(days=30)
        )
        
        return access_token, refresh_token
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()
