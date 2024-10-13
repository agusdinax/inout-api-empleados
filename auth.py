from sqlalchemy.orm import Session # type: ignore
from dbModels import User  # Asegúrate de que tienes un modelo User definido
from passlib.context import CryptContext # type: ignore

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user and pwd_context.verify(password, user.password):  # Verifica la contraseña
        return user
    return None
