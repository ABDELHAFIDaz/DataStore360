import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    user = os.getenv("PROJECT_DB_USER") or os.getenv("POSTGRES_USER")
    password = os.getenv("PROJECT_DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("PROJECT_DB_HOST") or os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("PROJECT_DB_PORT") or os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("PROJECT_DB_NAME") or os.getenv("POSTGRES_DB")

    connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(connection_string)