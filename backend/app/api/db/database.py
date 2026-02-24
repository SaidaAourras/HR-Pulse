# app/database.py (version simplifiée)
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# URL format: mssql+pyodbc://<user>:<pass>@<server>.database.windows.net/<db>?driver=ODBC+Driver+18+for+SQL+Server
DATABASE_URL = os.getenv("DATABASE_URL")

# engine = create_engine(
#     DATABASE_URL,
#     fast_executemany=True, # Optimisation pour les injections massives (Phase 2)
#     pool_pre_ping=True     # Important pour Azure SQL Serverless
# )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()