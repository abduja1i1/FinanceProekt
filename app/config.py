import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("POSTGRES_USER")
database = os.getenv("POSTGRES_DB")
password = os.getenv("POSTGRES_PASSWORD")
secret_key = os.getenv("SECRET_KEY")

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{user}:{password}@localhost:5432/{database}"
    SECRET_KEY = secret_key