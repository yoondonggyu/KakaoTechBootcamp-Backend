from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# TODO: Use environment variables for security
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost/FASTAPI_Project_DB"
# For local development (assuming root with no password for now, user can update)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:971201jcy!@localhost:3306/FASTAPI_Project_DB"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
