from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#SQL Database
#generates a .db file within the directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./stocks.db"

#creates engine based on URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
#Intermediary for connections to the database
#can add new objects, commit, or query to db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
