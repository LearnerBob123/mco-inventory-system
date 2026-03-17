import psycopg2

print("Trying to connect...")

connection = psycopg2.connect(
    "postgresql://postgres:-bqkCbFmjBxH%2A77@db.fmdrshndlqqimwhnsira.supabase.co:5432/postgres",
    connect_timeout=5
)

print("Connected successfully")