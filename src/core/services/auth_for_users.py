from sqlalchemy.orm import Session
from src.models.user import User
from src.core.services.security import verify_password


def validate_user(email: str, password: str, db: Session) -> bool:  # Проверка пользователя
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    return verify_password(password, user.password)
