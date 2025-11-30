from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import uuid

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
        
    user = User(email=email)
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # In a real app, verify password here. 
    # For this MVP, we might just issue a token for the email if it exists
    # or implement a magic link. For now, let's assume simple email login for testing.
    
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': access_token}), 200

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict()), 200

from app.services.gmail_service import GmailService
from flask import redirect, url_for

@bp.route('/gmail/authorize', methods=['GET'])
@jwt_required()
def gmail_authorize():
    user_id = get_jwt_identity()
    service = GmailService()
    
    # In a real app, we'd pass the user_id in the state to verify on callback
    # For now, we'll just redirect to the callback
    redirect_uri = url_for('auth.gmail_callback', _external=True)
    auth_url, state = service.get_authorization_url(redirect_uri)
    
    # Store state in session or db if needed for security
    
    return jsonify({'authorization_url': auth_url})

@bp.route('/gmail/callback', methods=['GET'])
def gmail_callback():
    # Note: In a real app, this endpoint would handle the code exchange
    # However, since we need to associate it with a logged-in user, 
    # and this is a callback from Google, we might need to handle the state parameter
    # to identify the user, or have the frontend handle the redirect and send the code to us.
    
    # For this MVP backend-only, we'll assume the user copies the code or we handle it here.
    # But wait, we need the user context.
    
    # Simplified flow:
    # 1. User calls /gmail/authorize -> gets URL
    # 2. User visits URL -> Google redirects to /gmail/callback?code=...
    # 3. We need to know WHICH user this is.
    
    # Let's grab the code and state
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({
        'message': 'Please copy this code and POST it to /api/auth/gmail/exchange',
        'code': code
    })

@bp.route('/gmail/exchange', methods=['POST'])
@jwt_required()
def gmail_exchange():
    user_id = get_jwt_identity()
    data = request.get_json()
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'Code is required'}), 400
        
    service = GmailService()
    # We need the same redirect_uri used in the authorize step
    redirect_uri = url_for('auth.gmail_callback', _external=True)
    
    try:
        credentials = service.get_credentials_from_code(code, redirect_uri)
        
        # Save credentials to user
        user = User.query.get(user_id)
        user.gmail_token = credentials.token
        user.gmail_refresh_token = credentials.refresh_token
        db.session.commit()
        
        return jsonify({'message': 'Gmail connected successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
