# test_connection.py
import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
else:
    print("Connecting to database...")

    try:
        connection = psycopg2.connect(DATABASE_URL, connect_timeout=5)
        print("Connected successfully")
    except OperationalError as e:
        print(f"Error: {e}")