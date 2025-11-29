# 🌐 Flask Domain Search Application with Authentication

A modern web application for searching domain information using the WhoisXML API, featuring **email/OTP authentication** and **OAuth 2.0 integration** for third-party applications like Lovable AI.

![Flask Domain Search](https://img.shields.io/badge/Flask-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### Domain Search
- 🔍 **Domain Lookup**: Detailed information about any domain
- 🎨 **Modern UI**: Beautiful dark theme with gradient effects
- 📱 **Responsive**: Works on desktop, tablet, and mobile

### Authentication System
- 📧 **Email/OTP Login**: Secure passwordless authentication
- 🔐 **JWT Tokens**: Industry-standard token-based auth
- ⏱️ **Rate Limiting**: Protection against abuse
- 🔄 **Token Refresh**: Seamless session management

### OAuth 2.0 Integration
- 🔗 **OAuth Provider**: Full OAuth 2.0 server implementation
- 🛡️ **PKCE Support**: Enhanced security for public clients
- 🌐 **Lovable AI Ready**: Pre-configured for Lovable AI integration
- 📊 **Multiple Scopes**: OpenID, profile, and email scopes

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- WhoisXML API key ([Get one here](https://whoisxmlapi.com/))
- Email service (Gmail/SMTP for production, console mode for development)

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd domain-search-app
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and configure:
   # - WHOISXML_API_KEY: Your WhoisXML API key
   # - SECRET_KEY: Random secret for Flask sessions
   # - JWT_SECRET_KEY: Random secret for JWT tokens
   # - EMAIL_BACKEND: 'console' for dev, 'smtp' for production
   # - EMAIL credentials if using SMTP
   ```

5. **Initialize the database**:
   ```bash
   python init_db.py
   ```
   
   **Important**: Save the OAuth credentials displayed! You'll need them for Lovable AI.

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Open your browser** and navigate to:
   ```
   http://localhost:5001
   ```

## 🔐 Authentication Flow

### Email/OTP Login

1. **Send OTP**: User enters email, receives 6-digit code
2. **Verify OTP**: User enters code, receives JWT tokens
3. **Access Protected Routes**: Use access token in Authorization header

```bash
# Example: Send OTP
curl -X POST http://localhost:5001/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'

# Example: Verify OTP
curl -X POST http://localhost:5001/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "otp": "123456"}'
```

### OAuth 2.0 Flow (for Lovable AI)

1. **Authorization**: Redirect user to `/oauth/authorize`
2. **User Consent**: User approves access
3. **Token Exchange**: Exchange authorization code for access token
4. **Access Resources**: Use access token to get user info

See [API_DOCS.md](API_DOCS.md) for complete OAuth integration guide.

## 🔑 OAuth Credentials for Lovable AI

After running `python init_db.py`, you'll receive:

- **Client ID**: Use in your Lovable AI OAuth configuration
- **Client Secret**: Keep this secure!
- **Redirect URIs**: Pre-configured for Lovable AI

### Add to Your Cloud Console

Add these redirect URLs to your OAuth provider:

```
http://localhost:5001/oauth/callback          # Development
https://your-domain.com/oauth/callback         # Production
https://lovable.ai/oauth/callback              # Lovable AI
```

## 📁 Project Structure

```
domain-search-app/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── models.py              # Database models (User, OTP, OAuth)
├── auth_service.py        # Authentication logic
├── email_service.py       # Email/OTP delivery
├── auth_routes.py         # Authentication endpoints
├── oauth_routes.py        # OAuth 2.0 endpoints
├── whois_client.py        # WhoisXML API client
├── init_db.py             # Database initialization
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── API_DOCS.md           # Complete API documentation
├── static/
│   ├── css/
│   │   └── style.css     # Modern dark theme styles
│   └── js/
│       └── script.js     # Frontend JavaScript
└── templates/
    └── index.html        # Main search page
```

## 🎯 API Endpoints

### Authentication
- `POST /auth/send-otp` - Send OTP to email
- `POST /auth/verify-otp` - Verify OTP and get tokens
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user info
- `POST /auth/logout` - Logout user

### OAuth 2.0
- `GET /oauth/authorize` - Authorization endpoint
- `POST /oauth/token` - Token exchange endpoint
- `GET /oauth/userinfo` - User information endpoint
- `POST /oauth/revoke` - Token revocation endpoint

### Domain Search
- `POST /search` - Search domain information
- `GET /health` - Health check endpoint

See [API_DOCS.md](API_DOCS.md) for detailed documentation with examples.

## 🛠️ Configuration

### Environment Variables

```env
# Flask
SECRET_KEY=your-secret-key
FLASK_DEBUG=True

# Database
DATABASE_URL=sqlite:///auth.db

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Email (Development)
EMAIL_BACKEND=console

# Email (Production - Gmail example)
EMAIL_BACKEND=smtp
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com

# CORS
CORS_ORIGINS=http://localhost:3000,https://lovable.ai

# WhoisXML API
WHOISXML_API_KEY=your_api_key_here
```

### Email Setup (Gmail)

For production with Gmail:

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use the app password in `EMAIL_PASSWORD`

## 🔧 Development

### Database Management

```bash
# Initialize database
python init_db.py

# The database file will be created at: auth.db
```

### Testing Authentication

```bash
# Test OTP flow
curl -X POST http://localhost:5001/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Check console for OTP code (in development mode)
# Then verify:
curl -X POST http://localhost:5001/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'
```

### Testing OAuth Flow

1. Open browser to:
   ```
   http://localhost:5001/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000/callback&scope=openid%20profile%20email
   ```

2. Enter email and authorize

3. Exchange code for token (see API_DOCS.md)

## 🔒 Security Features

- ✅ **Rate Limiting**: 5 OTP requests per email per hour
- ✅ **OTP Expiration**: Codes expire after 10 minutes
- ✅ **JWT Tokens**: Secure token-based authentication
- ✅ **CORS Protection**: Configurable allowed origins
- ✅ **PKCE Support**: Enhanced OAuth security
- ✅ **Password Hashing**: Bcrypt for secure password storage
- ✅ **HTTPS Ready**: Configure for production deployment

## 📊 Database Schema

### Users
- Email, verification status, timestamps

### OTPs
- Code, expiration, usage status

### OAuth Clients
- Client credentials, redirect URIs, scopes

### OAuth Tokens
- Access tokens, refresh tokens, expiration

## 🐛 Troubleshooting

### CORS Errors

Update `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,https://lovable.ai,https://your-frontend.com
```

### Email Not Sending

**Development**: Set `EMAIL_BACKEND=console` and check terminal output

**Production**: 
- Verify SMTP credentials
- Check firewall/port 587
- Use app-specific password for Gmail

### Database Errors

```bash
# Delete and reinitialize database
rm auth.db
python init_db.py
```

### Module Not Found

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 🚀 Production Deployment

1. **Set environment to production**:
   ```env
   FLASK_DEBUG=False
   EMAIL_BACKEND=smtp
   ```

2. **Use PostgreSQL** (recommended):
   ```env
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   ```

3. **Generate strong secrets**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Use HTTPS**: Configure SSL/TLS certificates

5. **Set up proper CORS**: Restrict to your domains only

## 📚 Documentation

- [API_DOCS.md](API_DOCS.md) - Complete API reference
- [WhoisXML API Docs](https://whoisxmlapi.com/documentation) - Domain API docs
- [OAuth 2.0 Spec](https://oauth.net/2/) - OAuth specification

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [WhoisXML API](https://whoisxmlapi.com/) for domain data
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Lovable AI](https://lovable.ai/) for frontend integration

---

**Built with ❤️ using Flask, JWT, and OAuth 2.0**
