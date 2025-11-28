#!/bin/bash

# PostgreSQL Setup Script for Anya.fi

echo "🔧 Setting up PostgreSQL for Anya.fi..."

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL is not running. Starting it..."
    echo "Please run: sudo systemctl start postgresql"
    echo "Then run this script again."
    exit 1
fi

# Database configuration
DB_NAME="anya_db"
DB_USER="anya_user"
DB_PASSWORD="anya_password"

echo "📊 Creating database and user..."

# Create user and database
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

-- Create database if not exists
SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

echo "✅ Database setup complete!"
echo ""
echo "📝 Update your .env file with:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost/$DB_NAME"
echo ""
echo "🚀 Next steps:"
echo "1. Update .env with the DATABASE_URL above"
echo "2. Run: source venv/bin/activate && alembic upgrade head"
