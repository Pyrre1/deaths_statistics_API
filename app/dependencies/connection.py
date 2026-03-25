import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()

def get_db_connection():
    """Open and return a psycopg connection with dict_row factory. Returns None on failure."""
    try:
        connection = psycopg.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            row_factory=dict_row # type: ignore
        )
        print("Connecting to:", os.getenv("DB_HOST"), os.getenv("DB_NAME"))
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# FastAPI dependency
# TODO: Implement connection pooling for better performance in production
# Current implementation creates new connection per request.
def get_db():
    """FastAPI dependency that yields a database connection and closes it after the request."""
    connection = get_db_connection()
    try:
        yield connection
    finally:
        if connection:
            connection.close()
