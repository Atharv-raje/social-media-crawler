import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database credentials
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER', 'Your_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Your_password')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("Connected to PostgreSQL")
        return conn
    except psycopg2.DatabaseError as e:
        print(f"Database connection error: {e}")
        return None
