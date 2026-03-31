import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("Trying to connect...")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL not set")

connection = psycopg2.connect(
    database_url,
    connect_timeout=5
)

print("Connected successfully")