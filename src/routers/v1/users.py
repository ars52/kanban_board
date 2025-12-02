from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from src.core.services.db import get_db
from src.infrastructure.jaminstance import jam
from src.models.user import User
from src.schemas.users import ProfileUpdateRequest, UserOut, UserUpdate
from typing import List
from src.crud.users import get_users, get_user, update_user, delete_user

router_users = APIRouter(prefix="/users", tags=["users"])


@router_users.patch("/me", response_model=UserOut)
async def update_my_profile(
    request: Request,
    payload: ProfileUpdateRequest,
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split('Bearer ')[-1] if auth_header else None
    if not token:
        raise HTTPException(status_code=401, detail='No token')
    try:
        token_payload = jam.verify_jwt_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

    email = token_payload.get('sub')
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(404, "User not found")

    if payload.first_name is not None:
        user.first_name = payload.first_name
    if payload.last_name is not None:
        user.last_name = payload.last_name
    if payload.middle_name is not None:
        user.middle_name = payload.middle_name
    if payload.gender is not None:
        user.gender = payload.gender

    db.commit()
    db.refresh(user)
    return user


@router_users.get("/", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_users(db, skip, limit)


@router_users.get("/{user_id}", response_model=UserOut)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router_users.put("/{user_id}", response_model=UserOut)
def update_user_endpoint(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = update_user(db, user_id, data)
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router_users.delete("/{user_id}", response_model=UserOut)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user
