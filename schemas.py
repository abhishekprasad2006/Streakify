from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: EmailStr


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    total_habits: Optional[int] = 0


class HabitCreate(BaseModel):
    name: str
    target_days_per_week: int
    user_id: int


class HabitResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    name: str
    target_days_per_week: int
    user_id: int
    is_active: Optional[bool] = True
    created_at: datetime


class HabitLogCreate(BaseModel):
    log_date: date
    completed: bool


class HabitLogUpdate(BaseModel):
    completed: bool


class HabitLogResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    habit_id: int
    log_date: date
    completed: bool
    created_at: datetime