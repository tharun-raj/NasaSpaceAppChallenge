import psycopg2

DB_CONFIG = {
    "dbname": "nasa_app",
    "user": "nasa_user",
    "password": "Root123",  # replace with actual password
    "host": "localhost",
    "port": "5432"
}

try:
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ Connected to PostgreSQL database!")
    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)
