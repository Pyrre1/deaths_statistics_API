import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        connection = psycopg.connect(
            host=os.getenv('DB_HOST'),
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT'),
            row_factory=dict_row
        )
        print("Connecting to:", os.getenv("DB_HOST"), os.getenv("DB_NAME"))
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

# FastAPI dependency
def get_db():
    connection = get_db_connection()
    try:
        yield connection
    finally:
        if connection:
            connection.close()