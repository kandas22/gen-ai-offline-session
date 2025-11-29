"""
Authentication routes for email/OTP login
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import timedelta
from models import db
from auth_service import AuthService
from email_service import EmailService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP to email address
    Request body: { "email": "user@example.com" }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        # Validate email
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Generate and send OTP
        success, message, otp_code = AuthService.send_otp(email)
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 429  # Too Many Requests
        
        # Send OTP via email
        email_success, email_message = EmailService.send_otp_email(email, otp_code)
        
        if not email_success:
            return jsonify({
                'success': False,
                'message': 'Failed to send OTP email'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'OTP sent to your email',
            'expires_in_minutes': AuthService.OTP_EXPIRY_MINUTES
        }), 200
        
    except Exception as e:
        print(f"Error in send_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while sending OTP'
        }), 500


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP and return JWT tokens
    Request body: { "email": "user@example.com", "otp": "123456" }
    """
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        otp_code = data.get('otp', '').strip()
        
        # Validate input
        if not email or not otp_code:
            return jsonify({
                'success': False,
                'message': 'Email and OTP are required'
            }), 400
        
        # Verify OTP
        success, message, user = AuthService.verify_otp(email, otp_code)
        
        if not success:
            return jsonify({
                'success': False,
                'message': message
            }), 401
        
        # Generate JWT tokens
        access_token, refresh_token = AuthService.generate_tokens(user)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during verification'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using refresh token
    Requires: Authorization header with refresh token
    """
    try:
        # Get user ID from JWT identity (it's a string)
        user_id = int(get_jwt_identity())
        
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Generate new access token
        access_token, _ = AuthService.generate_tokens(user)
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        print(f"Error in refresh: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to refresh token'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get current user information
    Requires: Authorization header with access token
    """
    try:
        # Get user ID from JWT identity (it's a string)
        user_id = int(get_jwt_identity())
        
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get user information'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout user (client should delete tokens)
    Requires: Authorization header with access token
    """
    # In a production app, you might want to blacklist the token
    # For now, we'll just return success and let the client delete the token
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200
