from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


class ProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[str] = None


# for crud
class UserBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    gender: Optional[str] = None
    email: str


class UserUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    gender: Optional[str]
    email: Optional[EmailStr]


class UserOut(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
