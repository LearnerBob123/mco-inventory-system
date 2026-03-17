import psycopg2
from psycopg2 import OperationalError

print("Connecting to database...")

try:
    connection = psycopg2.connect(
        "postgresql://postgres:-bqkCbFmjBxH%2A77@db.fmdrshndlqqimwhnsira.supabase.co:5432/postgres",
        connect_timeout=5
    )
    print("Connected successfully")
except OperationalError as e:
    print(f"Error: {e}")