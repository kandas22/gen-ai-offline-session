# API Documentation

Complete API reference for the Domain Search Application with Authentication and OAuth 2.0.

## Base URL

```
Development: http://localhost:5001
Production: https://your-domain.com
```

---

## Authentication APIs

### 1. Send OTP

Send a one-time password to the user's email for authentication.

**Endpoint:** `POST /auth/send-otp`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "OTP sent to your email",
  "expires_in_minutes": 10
}
```

**Error Response (429 Too Many Requests):**
```json
{
  "success": false,
  "message": "Too many OTP requests. Please try again later."
}
```

**Rate Limit:** 5 OTP requests per email per hour

---

### 2. Verify OTP

Verify the OTP code and receive JWT authentication tokens.

**Endpoint:** `POST /auth/verify-otp`

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_verified": true,
    "created_at": "2025-11-29T12:00:00",
    "last_login": "2025-11-29T12:30:00"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Invalid or expired OTP"
}
```

**Token Expiration:**
- Access Token: 24 hours
- Refresh Token: 30 days

---

### 3. Refresh Token

Get a new access token using a refresh token.

**Endpoint:** `POST /auth/refresh`

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 4. Get Current User

Retrieve information about the currently authenticated user.

**Endpoint:** `GET /auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_verified": true,
    "created_at": "2025-11-29T12:00:00",
    "last_login": "2025-11-29T12:30:00"
  }
}
```

---

### 5. Logout

Logout the current user (client should delete stored tokens).

**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## OAuth 2.0 APIs

### 1. Authorization Endpoint

Initiate the OAuth 2.0 authorization code flow.

**Endpoint:** `GET /oauth/authorize`

**Query Parameters:**
- `response_type` (required): Must be `code`
- `client_id` (required): OAuth client ID
- `redirect_uri` (required): Callback URL (must be pre-registered)
- `scope` (optional): Space-separated scopes (default: `openid profile email`)
- `state` (recommended): CSRF protection token
- `code_challenge` (optional): PKCE challenge
- `code_challenge_method` (optional): `S256` or `plain`

**Example:**
```
GET /oauth/authorize?response_type=code&client_id=abc123&redirect_uri=https://lovable.ai/oauth/callback&scope=openid%20profile%20email&state=xyz789
```

**Response:**
Redirects to `redirect_uri` with authorization code:
```
https://lovable.ai/oauth/callback?code=AUTH_CODE&state=xyz789
```

**Supported Scopes:**
- `openid`: OpenID Connect authentication
- `profile`: User profile information
- `email`: User email address

---

### 2. Token Endpoint

Exchange authorization code for access token.

**Endpoint:** `POST /oauth/token`

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body (Authorization Code Grant):**
```
grant_type=authorization_code
&code=AUTH_CODE
&redirect_uri=https://lovable.ai/oauth/callback
&client_id=abc123
&client_secret=secret123
&code_verifier=VERIFIER (if PKCE used)
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "openid profile email"
}
```

**Request Body (Refresh Token Grant):**
```
grant_type=refresh_token
&refresh_token=REFRESH_TOKEN
&client_id=abc123
&client_secret=secret123
```

---

### 3. UserInfo Endpoint

Get user information using an access token.

**Endpoint:** `GET /oauth/userinfo`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "sub": "1",
  "email": "user@example.com",
  "email_verified": true,
  "name": "user",
  "updated_at": 1732872600
}
```

**Fields returned based on scopes:**
- `openid`: `sub` (user ID)
- `email`: `email`, `email_verified`
- `profile`: `name`, `updated_at`

---

### 4. Token Revocation Endpoint

Revoke an access or refresh token.

**Endpoint:** `POST /oauth/revoke`

**Content-Type:** `application/x-www-form-urlencoded`

**Request Body:**
```
token=TOKEN_TO_REVOKE
&client_id=abc123
&client_secret=secret123
```

**Response (200 OK):**
```
(Empty response)
```

---

## Domain Search APIs

### Search Domain

Search for domain information using WhoisXML API.

**Endpoint:** `POST /search`

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "domain": "example.com",
  "data": {
    "registrar": "Example Registrar",
    "created_date": "1995-08-14",
    "expiry_date": "2025-08-13",
    "status": "active"
  }
}
```

---

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid or missing authentication |
| 404 | Not Found - Resource doesn't exist |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |

---

## Rate Limiting

Default rate limits:
- **Global**: 100 requests per hour per IP
- **OTP Sending**: 5 requests per email per hour
- **OAuth Authorization**: 10 requests per minute per IP

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1732876200
```

---

## Integration Example (Lovable AI)

### Step 1: Get OAuth Credentials

Run the database initialization script to get your OAuth credentials:

```bash
python init_db.py
```

Save the `client_id` and `client_secret` provided.

### Step 2: Configure Redirect URI

Add your Lovable AI callback URL to your cloud console:
```
https://lovable.ai/oauth/callback
```

### Step 3: Authorization Flow

1. **Redirect user to authorization endpoint:**
```
https://your-domain.com/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://lovable.ai/oauth/callback&scope=openid%20profile%20email&state=RANDOM_STATE
```

2. **User authenticates and approves**

3. **Receive authorization code:**
```
https://lovable.ai/oauth/callback?code=AUTH_CODE&state=RANDOM_STATE
```

4. **Exchange code for token:**
```bash
curl -X POST https://your-domain.com/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=https://lovable.ai/oauth/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

5. **Get user info:**
```bash
curl -X GET https://your-domain.com/oauth/userinfo \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

---

## Security Best Practices

1. **Always use HTTPS in production**
2. **Store client secrets securely**
3. **Implement PKCE for public clients**
4. **Validate redirect URIs strictly**
5. **Use short-lived access tokens**
6. **Implement token rotation**
7. **Monitor for suspicious activity**
8. **Use strong JWT secrets**

---

## Testing with cURL

### Test OTP Flow

```bash
# Send OTP
curl -X POST http://localhost:5001/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# Verify OTP (check console for OTP code)
curl -X POST http://localhost:5001/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'

# Get user info
curl -X GET http://localhost:5001/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test OAuth Flow

```bash
# Get authorization URL (open in browser)
http://localhost:5001/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:3000/callback&scope=openid%20profile%20email

# Exchange code for token
curl -X POST http://localhost:5001/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=http://localhost:3000/callback" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```
