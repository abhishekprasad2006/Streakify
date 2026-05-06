from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
import services.habit_service as habit_service
from database import SessionLocal

router = APIRouter(prefix="/habits", tags=["Habits"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=schemas.HabitResponse, status_code=201)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    return habit_service.create_habit(
        db,
        habit.name,
        habit.target_days_per_week,
        habit.user_id
    )


@router.delete("/{habit_id}")
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    return habit_service.delete_habit(db, habit_id)
