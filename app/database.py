import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    """Returns a new database connection."""
    return psycopg2.connect(DATABASE_URL)