from pydantic import BaseModel
from typing import Optional
import datetime


class TaskBase(BaseModel):
    column_id:   int
    created_by:  int
    assigned_to: int
    title:        str
    description:  str
    is_finished:  bool = False
    position:     int = 0


class TaskCreate(BaseModel):
    column_id:   int
    title:       str
    description: str
    assigned_to: Optional[int] = None


class TaskUpdate(BaseModel):
    column_id:   Optional[int] = None
    created_by:  Optional[int] = None
    assigned_to: Optional[int] = None
    title:        Optional[str] = None
    description:  Optional[str] = None
    is_finished:  Optional[bool] = None
    position:     Optional[int] = None
    finished_at:  Optional[datetime.datetime] = None


class TaskOut(TaskBase):
    id:           int
    created_at:   datetime.datetime
    finished_at:  Optional[datetime.datetime]

    model_config = {"from_attributes": True}
