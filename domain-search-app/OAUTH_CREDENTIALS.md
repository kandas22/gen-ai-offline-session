# 🔑 OAuth Credentials for Lovable AI

## Lovable AI OAuth Client

**Client ID:**
```
9eCGvEB0YjgIDyY8LH7Xh4uWQbOmZyys
```

**Client Secret:**
```
aMtPJTHlZwF707iEvtvx_o1hFc9jgvv13h8hZcm5fyVhvmUPIR_H99Mdqapif5aC
```

## Authorized Redirect URIs

Add these to your cloud console (Google, GitHub, etc.):

```
http://localhost:5001/auth/callback
http://localhost:3000/auth/callback
https://lovable.ai/oauth/callback
https://lovable.dev/oauth/callback
```

## OAuth Endpoints

**Authorization Endpoint:**
```
http://localhost:5001/oauth/authorize
```

**Token Endpoint:**
```
http://localhost:5001/oauth/token
```

**UserInfo Endpoint:**
```
http://localhost:5001/oauth/userinfo
```

**Revoke Endpoint:**
```
http://localhost:5001/oauth/revoke
```

## Allowed Scopes

- `openid` - OpenID Connect authentication
- `profile` - User profile information  
- `email` - User email address

## Example Authorization URL

```
http://localhost:5001/oauth/authorize?response_type=code&client_id=9eCGvEB0YjgIDyY8LH7Xh4uWQbOmZyys&redirect_uri=https://lovable.ai/oauth/callback&scope=openid%20profile%20email&state=RANDOM_STATE
```

## Production URLs

When deploying to production, update these URLs:

**Authorization:**
```
https://your-domain.com/oauth/authorize
```

**Token:**
```
https://your-domain.com/oauth/token
```

**UserInfo:**
```
https://your-domain.com/oauth/userinfo
```

---

⚠️ **IMPORTANT:** Keep the client secret secure! Never commit it to version control or share it publicly.
