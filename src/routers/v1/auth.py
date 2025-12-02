from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src.infrastructure.jaminstance import jam
from src.core.services.db import get_db
from src.models.user import User
from src.schemas.auth import LoginRequest, RegisterRequest
from src.schemas.users import UserOut
from src.core.services.auth_for_users import validate_user
from src.crud.users import create_user_raw

auth = APIRouter(prefix="/auth", tags=["auth"])


@auth.post("/login", status_code=status.HTTP_200_OK)
async def log_in(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    if not validate_user(request.email, request.password, db):
        raise HTTPException(
            status_code=401,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # токен с email в payload
    token = jam.gen_jwt_token({"sub": request.email})

    # Try to return basic user info so frontend can set id immediately
    user = db.query(User).filter(User.email == request.email).first()
    user_out = None
    if user:
        # rely on pydantic model to serialize
        from src.schemas.users import UserOut as _UserOut
        # SQLAlchemy model -> pydantic: use from_attributes=True to read attributes
        user_out = _UserOut.model_validate(user, from_attributes=True)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_out
    }


@auth.post("/register")
async def register_init(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    # Проверка существования пользователя
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(400, "Почта уже зарегистрирована")

    user = create_user_raw(db, email=request.email, password=request.password)
    return {"status": "ok"}



@auth.get('/me', response_model=UserOut)
def me(request: Request, db: Session = Depends(get_db)):
    # Try to extract token from Authorization header
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split('Bearer ')[-1] if auth_header else None
    if not token:
        raise HTTPException(status_code=401, detail='No token')
    try:
        payload = jam.verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    # payload may contain user_id or sub (email)
    user = None
    if 'user_id' in payload:
        user = db.query(User).filter(User.id == payload['user_id']).first()
    else:
        email = payload.get('sub')
        if email:
            user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    # return pydantic-validated user object (use from_attributes for ORM instance)
    return UserOut.model_validate(user, from_attributes=True)
