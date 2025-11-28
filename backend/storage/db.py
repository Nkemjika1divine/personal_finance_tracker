from dotenv import load_dotenv
from models.basemodel import Base
from models.user import User
from models.budget import Budget
from models.category import Category
from models.expense import Expense
from models.income import Income
from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

PFT_DB = environ.get("PFT_DB")
PFT_PORT = environ.get("PFT_PORT")
PFT_USER = environ.get("PFT_USER")
PFT_PWD = environ.get("PFT_PWD")
PFT_HOST = environ.get("PFT_HOST")

if not all([PFT_DB, PFT_PORT, PFT_USER, PFT_PWD, PFT_HOST]):
    raise ValueError("One or more environment variables are missing")

database_url = "mysql+pymysql://{}:{}@{}:{}/{}".format(
    PFT_USER, PFT_PWD, PFT_HOST, PFT_PORT, PFT_DB
)
engine = create_engine(database_url, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
