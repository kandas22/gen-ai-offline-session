# 🚀 Supabase Migration Guide

## Current Status

✅ **App is running with SQLite** (automatic fallback)  
⚠️ **Supabase connection failed** - needs correct credentials

## Why Supabase?

- **Scalable PostgreSQL** database in the cloud
- **Real-time capabilities** for future features
- **Built-in authentication** (optional integration)
- **Free tier** available
- **Better for production** than SQLite

## Quick Fix: Get Correct Connection String

### Step 1: Access Supabase Dashboard

1. Go to https://supabase.com/dashboard
2. Log in to your account
3. Select your project: `ieyumjrmncihgcyhwdpo`

### Step 2: Get Connection String

1. Click **Settings** (gear icon) in the left sidebar
2. Click **Database**
3. Scroll down to **Connection string**
4. Select **URI** tab
5. Copy the connection string

**It should look like:**
```
postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

### Step 3: Update .env File

Open your `.env` file and update the `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Important:**
- Replace `[YOUR-PASSWORD]` with your actual database password
- Use port **6543** (connection pooler) for better performance
- Or use port **5432** (direct connection)

### Step 4: Restart the App

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python app.py
```

You should see:
```
✅ Supabase PostgreSQL connection successful
✅ Database tables created in Supabase PostgreSQL
```

---

## Alternative: Reset Database Password

If you don't know your database password:

### Option 1: Reset in Dashboard

1. Go to Supabase Dashboard → Settings → Database
2. Scroll to **Database Password**
3. Click **Reset database password**
4. Copy the new password
5. Update your `.env` file with the new connection string

### Option 2: Use Environment Variables

Supabase provides connection details as separate variables:

```bash
# In your Supabase Dashboard → Settings → Database
SUPABASE_DB_HOST=db.ieyumjrmncihgcyhwdpo.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=your-password-here

# Then construct the URL:
DATABASE_URL=postgresql://${SUPABASE_DB_USER}:${SUPABASE_DB_PASSWORD}@${SUPABASE_DB_HOST}:${SUPABASE_DB_PORT}/${SUPABASE_DB_NAME}
```

---

## Migration Steps (Once Connected)

### 1. Run Migration Script

```bash
python migrate_to_supabase.py
```

This will:
- Create all database tables in Supabase
- Set up OAuth clients
- Display OAuth credentials

### 2. Verify Tables

In Supabase Dashboard:
1. Go to **Table Editor**
2. You should see these tables:
   - `users`
   - `otps`
   - `oauth_clients`
   - `oauth_authorization_codes`
   - `oauth_access_tokens`

### 3. Test the Connection

```bash
# Test authentication
curl -X POST http://localhost:5001/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

---

## Connection String Formats

### Direct Connection (Port 5432)
```
postgresql://postgres:PASSWORD@db.PROJECT-REF.supabase.co:5432/postgres
```

**Pros:** Simple, direct  
**Cons:** Limited connections, slower for many requests

### Connection Pooler (Port 6543) - Recommended
```
postgresql://postgres.PROJECT-REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
```

**Pros:** Better performance, handles more connections  
**Cons:** Slightly more complex URL

### Session Mode (Port 5432)
```
postgresql://postgres:PASSWORD@db.PROJECT-REF.supabase.co:5432/postgres?pgbouncer=true
```

**Pros:** Long-running connections  
**Cons:** Not recommended for SQLAlchemy

---

## Troubleshooting

### Error: "password authentication failed"

**Solution:**
1. Reset your database password in Supabase dashboard
2. Update `.env` with the new password
3. Restart the app

### Error: "Connection refused"

**Possible causes:**
1. Supabase project is paused (free tier)
2. Network/firewall blocking connection
3. Incorrect host/port

**Solution:**
1. Check if project is active in Supabase dashboard
2. Try direct connection (port 5432)
3. Check your internet connection

### Error: "SSL required"

**Solution:**
Add `?sslmode=require` to your connection string:
```
postgresql://postgres:PASSWORD@db.PROJECT-REF.supabase.co:5432/postgres?sslmode=require
```

### App Still Uses SQLite

**Check:**
1. Is `DATABASE_URL` set in `.env`?
2. Is the connection string correct?
3. Did you restart the app after updating `.env`?

---

## Current Fallback Behavior

The app is designed to **automatically fall back to SQLite** if Supabase connection fails:

```
🔗 Attempting to connect to Supabase PostgreSQL...
⚠️  Supabase PostgreSQL connection failed
🔄 Falling back to SQLite...
✅ Using SQLite database
```

This means:
- ✅ App always works (even without Supabase)
- ✅ No manual intervention needed
- ✅ Easy to switch between SQLite and Supabase
- ⚠️ SQLite data won't transfer to Supabase automatically

---

## Benefits of Using Supabase

| Feature | SQLite | Supabase |
|---------|--------|----------|
| **Scalability** | Limited | Unlimited |
| **Concurrent Users** | ~100 | Thousands |
| **Backups** | Manual | Automatic |
| **Real-time** | No | Yes |
| **Cloud Access** | No | Yes |
| **Production Ready** | No | Yes |

---

## Next Steps

1. **Get correct Supabase connection string**
2. **Update `.env` file**
3. **Restart the app**
4. **Run migration**: `python migrate_to_supabase.py`
5. **Test authentication endpoints**

---

## Need Help?

If you're still having issues:

1. Share the **exact error message**
2. Confirm your **Supabase project is active**
3. Try **resetting the database password**
4. Check if **port 5432 or 6543 is accessible**

The app will continue to work with SQLite until Supabase is properly configured!
