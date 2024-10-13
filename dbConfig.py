from fastapi import FastAPI # type: ignore
from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from dotenv import load_dotenv # type: ignore
import os

load_dotenv()
app = FastAPI()

# Configuración de la base de datos
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
    f"{os.getenv('DATABASE_HOST')}/{os.getenv('DATABASE_NAME')}"
)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
