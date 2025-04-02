from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
import os

Base = declarative_base()

# SQLite engine and session
home_dir = os.path.expanduser("~")
DATABASE_URL = f"sqlite:///{os.path.join(home_dir, 'ai-agent.sqlite3db')}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_v2():
    while True:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

def bind_service(Service: any):
    def get_service(db: Session = Depends(get_db)):
        return Service(db)

    return get_service
