#!/bin/bash
# Script to update .env file with Supabase credentials

ENV_FILE=".env"

# Supabase connection string
SUPABASE_URL="postgresql://postgres:CqArIPiNBIHwuuYV@db.ieyumjrmncihgcyhwdpo.supabase.co:5432/postgres"

echo "🔧 Updating .env file with Supabase credentials..."

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Update or add DATABASE_URL
if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
    # Update existing DATABASE_URL
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=$SUPABASE_URL|" "$ENV_FILE"
    else
        # Linux
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=$SUPABASE_URL|" "$ENV_FILE"
    fi
    echo "✅ Updated DATABASE_URL in .env"
else
    # Add DATABASE_URL
    echo "" >> "$ENV_FILE"
    echo "# Supabase Database" >> "$ENV_FILE"
    echo "DATABASE_URL=$SUPABASE_URL" >> "$ENV_FILE"
    echo "✅ Added DATABASE_URL to .env"
fi

echo ""
echo "✅ .env file updated successfully!"
echo ""
echo "Next steps:"
echo "1. Run: python migrate_to_supabase.py"
echo "2. Restart your Flask app"
echo ""
