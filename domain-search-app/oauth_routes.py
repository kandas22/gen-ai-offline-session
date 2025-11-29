"""
OAuth 2.0 routes for third-party application integration (e.g., Lovable AI)
"""
from flask import Blueprint, request, jsonify, redirect, render_template_string
from datetime import datetime, timedelta
import secrets
import hashlib
import base64
import json
from models import db, User, OAuthClient, OAuthAuthorizationCode, OAuthAccessToken
from auth_service import AuthService

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')


def generate_token(length=48):
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


@oauth_bp.route('/authorize', methods=['GET'])
def authorize():
    """
    OAuth 2.0 Authorization Endpoint
    
    Query parameters:
    - response_type: 'code' (required)
    - client_id: OAuth client ID (required)
    - redirect_uri: Callback URL (required)
    - scope: Requested scopes (optional, default: 'openid profile email')
    - state: CSRF token (recommended)
    - code_challenge: PKCE challenge (optional)
    - code_challenge_method: 'S256' or 'plain' (optional)
    """
    try:
        # Get parameters
        response_type = request.args.get('response_type')
        client_id = request.args.get('client_id')
        redirect_uri = request.args.get('redirect_uri')
        scope = request.args.get('scope', 'openid profile email')
        state = request.args.get('state', '')
        code_challenge = request.args.get('code_challenge')
        code_challenge_method = request.args.get('code_challenge_method', 'S256')
        
        # Validate required parameters
        if response_type != 'code':
            return jsonify({
                'error': 'unsupported_response_type',
                'error_description': 'Only authorization code flow is supported'
            }), 400
        
        if not client_id or not redirect_uri:
            return jsonify({
                'error': 'invalid_request',
                'error_description': 'client_id and redirect_uri are required'
            }), 400
        
        # Validate client
        client = OAuthClient.query.filter_by(client_id=client_id).first()
        if not client:
            return jsonify({
                'error': 'invalid_client',
                'error_description': 'Invalid client_id'
            }), 401
        
        # Validate redirect URI
        if not client.check_redirect_uri(redirect_uri):
            return jsonify({
                'error': 'invalid_request',
                'error_description': 'Invalid redirect_uri'
            }), 400
        
        # For this demo, we'll auto-approve for authenticated users
        # In production, you'd show a consent screen
        
        # Get user from session/token (for demo, we'll create a mock user)
        # In production, user should be authenticated before reaching here
        user_email = request.args.get('user_email')  # Demo parameter
        
        if not user_email:
            # Return a simple login form
            login_form = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login - OAuth Authorization</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        max-width: 400px;
                        width: 100%;
                    }}
                    h1 {{
                        color: #333;
                        margin-bottom: 10px;
                        font-size: 24px;
                    }}
                    .client-info {{
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                    }}
                    .client-info p {{
                        margin: 5px 0;
                        color: #666;
                        font-size: 14px;
                    }}
                    .scope-list {{
                        list-style: none;
                        padding: 0;
                        margin: 15px 0;
                    }}
                    .scope-list li {{
                        padding: 8px 0;
                        border-bottom: 1px solid #eee;
                        color: #555;
                    }}
                    .scope-list li:last-child {{
                        border-bottom: none;
                    }}
                    input[type="email"] {{
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #ddd;
                        border-radius: 6px;
                        font-size: 16px;
                        box-sizing: border-box;
                        margin: 10px 0;
                    }}
                    input[type="email"]:focus {{
                        outline: none;
                        border-color: #667eea;
                    }}
                    button {{
                        width: 100%;
                        padding: 12px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: transform 0.2s;
                    }}
                    button:hover {{
                        transform: translateY(-2px);
                    }}
                    .warning {{
                        background: #fff3cd;
                        border-left: 4px solid #ffc107;
                        padding: 12px;
                        margin: 20px 0;
                        border-radius: 4px;
                        font-size: 14px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 Authorization Required</h1>
                    <div class="client-info">
                        <p><strong>Application:</strong> {client.client_name}</p>
                        <p><strong>Requesting access to:</strong></p>
                        <ul class="scope-list">
                            {''.join(f'<li>✓ {s.strip()}</li>' for s in scope.split())}
                        </ul>
                    </div>
                    <form method="GET" action="/oauth/authorize">
                        <input type="hidden" name="response_type" value="{response_type}">
                        <input type="hidden" name="client_id" value="{client_id}">
                        <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                        <input type="hidden" name="scope" value="{scope}">
                        <input type="hidden" name="state" value="{state}">
                        {f'<input type="hidden" name="code_challenge" value="{code_challenge}">' if code_challenge else ''}
                        {f'<input type="hidden" name="code_challenge_method" value="{code_challenge_method}">' if code_challenge else ''}
                        
                        <label for="email">Enter your email to continue:</label>
                        <input type="email" id="email" name="user_email" placeholder="your@email.com" required>
                        
                        <button type="submit">Authorize</button>
                    </form>
                    <div class="warning">
                        <strong>⚠️ Demo Mode:</strong> In production, you would authenticate via OTP first.
                    </div>
                </div>
            </body>
            </html>
            """
            return render_template_string(login_form)
        
        # Get or create user
        user = AuthService.create_or_get_user(user_email)
        
        # Generate authorization code
        auth_code = generate_token(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        authorization = OAuthAuthorizationCode(
            code=auth_code,
            client_id=client_id,
            user_id=user.id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            expires_at=expires_at
        )
        db.session.add(authorization)
        db.session.commit()
        
        # Redirect back to client with authorization code
        separator = '&' if '?' in redirect_uri else '?'
        redirect_url = f"{redirect_uri}{separator}code={auth_code}"
        if state:
            redirect_url += f"&state={state}"
        
        return redirect(redirect_url)
        
    except Exception as e:
        print(f"Error in authorize: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'error_description': 'An error occurred during authorization'
        }), 500


@oauth_bp.route('/token', methods=['POST'])
def token():
    """
    OAuth 2.0 Token Endpoint
    
    Request body (form-encoded):
    - grant_type: 'authorization_code' or 'refresh_token' (required)
    - code: Authorization code (required for authorization_code)
    - redirect_uri: Same as authorization request (required for authorization_code)
    - client_id: OAuth client ID (required)
    - client_secret: OAuth client secret (required)
    - code_verifier: PKCE verifier (optional)
    - refresh_token: Refresh token (required for refresh_token grant)
    """
    try:
        # Get parameters (form-encoded)
        grant_type = request.form.get('grant_type')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        
        # Validate client credentials
        client = OAuthClient.query.filter_by(client_id=client_id).first()
        if not client or not client.check_client_secret(client_secret):
            return jsonify({
                'error': 'invalid_client',
                'error_description': 'Invalid client credentials'
            }), 401
        
        if grant_type == 'authorization_code':
            return handle_authorization_code_grant(client)
        elif grant_type == 'refresh_token':
            return handle_refresh_token_grant(client)
        else:
            return jsonify({
                'error': 'unsupported_grant_type',
                'error_description': 'Only authorization_code and refresh_token grants are supported'
            }), 400
            
    except Exception as e:
        print(f"Error in token: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'error_description': 'An error occurred during token exchange'
        }), 500


def handle_authorization_code_grant(client):
    """Handle authorization code grant"""
    code = request.form.get('code')
    redirect_uri = request.form.get('redirect_uri')
    code_verifier = request.form.get('code_verifier')
    
    # Validate authorization code
    authorization = OAuthAuthorizationCode.query.filter_by(
        code=code,
        client_id=client.client_id
    ).first()
    
    if not authorization or not authorization.is_valid():
        return jsonify({
            'error': 'invalid_grant',
            'error_description': 'Invalid or expired authorization code'
        }), 400
    
    # Validate redirect URI
    if authorization.redirect_uri != redirect_uri:
        return jsonify({
            'error': 'invalid_grant',
            'error_description': 'Redirect URI mismatch'
        }), 400
    
    # Validate PKCE if used
    if authorization.code_challenge:
        if not code_verifier:
            return jsonify({
                'error': 'invalid_request',
                'error_description': 'code_verifier is required'
            }), 400
        
        # Verify code challenge
        if authorization.code_challenge_method == 'S256':
            verifier_hash = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode()).digest()
            ).decode().rstrip('=')
            if verifier_hash != authorization.code_challenge:
                return jsonify({
                    'error': 'invalid_grant',
                    'error_description': 'Invalid code_verifier'
                }), 400
        elif authorization.code_challenge != code_verifier:
            return jsonify({
                'error': 'invalid_grant',
                'error_description': 'Invalid code_verifier'
            }), 400
    
    # Mark code as used
    authorization.is_used = True
    
    # Generate tokens
    access_token = generate_token(48)
    refresh_token = generate_token(48)
    
    token_record = OAuthAccessToken(
        access_token=access_token,
        refresh_token=refresh_token,
        client_id=client.client_id,
        user_id=authorization.user_id,
        scope=authorization.scope,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        refresh_token_expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(token_record)
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'refresh_token': refresh_token,
        'scope': authorization.scope
    }), 200


def handle_refresh_token_grant(client):
    """Handle refresh token grant"""
    refresh_token = request.form.get('refresh_token')
    
    # Find token record
    token_record = OAuthAccessToken.query.filter_by(
        refresh_token=refresh_token,
        client_id=client.client_id
    ).first()
    
    if not token_record or token_record.revoked:
        return jsonify({
            'error': 'invalid_grant',
            'error_description': 'Invalid refresh token'
        }), 400
    
    # Check if refresh token is expired
    if datetime.utcnow() > token_record.refresh_token_expires_at:
        return jsonify({
            'error': 'invalid_grant',
            'error_description': 'Refresh token expired'
        }), 400
    
    # Generate new access token
    new_access_token = generate_token(48)
    token_record.access_token = new_access_token
    token_record.expires_at = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()
    
    return jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'scope': token_record.scope
    }), 200


@oauth_bp.route('/userinfo', methods=['GET'])
def userinfo():
    """
    OAuth 2.0 UserInfo Endpoint
    
    Headers:
    - Authorization: Bearer <access_token>
    """
    try:
        # Get access token from header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Invalid authorization header'
            }), 401
        
        access_token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Validate token
        token_record = OAuthAccessToken.query.filter_by(access_token=access_token).first()
        if not token_record or not token_record.is_valid():
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'Invalid or expired access token'
            }), 401
        
        # Get user
        user = User.query.get(token_record.user_id)
        if not user:
            return jsonify({
                'error': 'invalid_token',
                'error_description': 'User not found'
            }), 404
        
        # Return user info based on scopes
        scopes = token_record.scope.split()
        user_info = {}
        
        if 'openid' in scopes:
            user_info['sub'] = str(user.id)
        
        if 'email' in scopes:
            user_info['email'] = user.email
            user_info['email_verified'] = user.is_verified
        
        if 'profile' in scopes:
            user_info['name'] = user.email.split('@')[0]  # Use email prefix as name
            user_info['updated_at'] = int(user.last_login.timestamp()) if user.last_login else None
        
        return jsonify(user_info), 200
        
    except Exception as e:
        print(f"Error in userinfo: {str(e)}")
        return jsonify({
            'error': 'server_error',
            'error_description': 'An error occurred while fetching user info'
        }), 500


@oauth_bp.route('/revoke', methods=['POST'])
def revoke():
    """
    OAuth 2.0 Token Revocation Endpoint
    
    Request body (form-encoded):
    - token: Access or refresh token to revoke
    - client_id: OAuth client ID
    - client_secret: OAuth client secret
    """
    try:
        token = request.form.get('token')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        
        # Validate client
        client = OAuthClient.query.filter_by(client_id=client_id).first()
        if not client or not client.check_client_secret(client_secret):
            return jsonify({
                'error': 'invalid_client',
                'error_description': 'Invalid client credentials'
            }), 401
        
        # Find and revoke token
        token_record = OAuthAccessToken.query.filter(
            (OAuthAccessToken.access_token == token) | (OAuthAccessToken.refresh_token == token),
            OAuthAccessToken.client_id == client_id
        ).first()
        
        if token_record:
            token_record.revoked = True
            db.session.commit()
        
        # Always return 200 per OAuth spec
        return '', 200
        
    except Exception as e:
        print(f"Error in revoke: {str(e)}")
        return '', 200  # Still return 200 per spec
