# Subscription Usage Tracker API

A Flask-based backend service for tracking and validating entertainment subscription usage. This service integrates with Gmail to parse subscription emails, tracks usage logs, and provides analytics on subscription effectiveness.

## Prerequisites

- Python 3.8 or higher
- Redis (for caching)
  - **Mac**: `brew install redis` then `brew services start redis`
  - **Windows**: [Install WSL](https://redis.io/docs/install/install-redis/install-redis-on-windows/) or use Docker
- A Supabase account (or any PostgreSQL database)
- Google Cloud Console project (for Gmail API)

## Step-by-Step Setup Guide

### 1. Environment Setup

Navigate to the project directory:
```bash
cd subscriptions_backend
```

Create and activate a virtual environment:
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration

The project uses a `.env` file for configuration. A `.env` file has been pre-configured with default settings and your Supabase connection string.

If you need to customize it, edit the `.env` file:
```bash
# Database Connection
DATABASE_URL=postgresql://postgres:CqArIPiNBlHwuuYV@db.ieyumjrmncihgcyhwdpo.supabase.co:5432/postgres

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your_secure_secret_key

# Google / Gmail API (Required for email parsing)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

### 3. Database Initialization

Initialize the database tables in Supabase:
```bash
python init_db.py
```
This script will create the `users`, `subscriptions`, and `usage_logs` tables.

### 4. Running the Application

Start the Flask development server:
```bash
python run.py
```
The server will start at `http://localhost:5001`.

### 5. API Documentation

Once the server is running, you can access the interactive Swagger UI documentation at:
- **URL**: [http://localhost:5001/api/docs](http://localhost:5001/api/docs)

This UI allows you to explore endpoints, see request/response schemas, and test API calls directly.

### 6. Testing the Flow

A verification script is included to test the core flow (Register -> Login -> Create Subscription -> Check Analytics):

```bash
python verify_flow.py
```

## Gmail Integration Setup

To enable the automatic email parsing feature:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable the **Gmail API**.
4. Go to **Credentials** -> **Create Credentials** -> **OAuth client ID**.
5. Select **Web application**.
6. Add `http://localhost:5001/api/auth/gmail/callback` to **Authorized redirect URIs**.
7. Copy the **Client ID** and **Client Secret** to your `.env` file.

## Project Structure

- `app/`: Core application code
  - `models/`: Database models (SQLAlchemy)
  - `routes/`: API endpoints (Blueprints)
  - `services/`: Business logic (Gmail, Analytics, Parser)
- `migrations/`: Database migration scripts
- `tests/`: Automated tests
- `swagger.yaml`: OpenAPI specification
