from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
import schemas
import services.log_service as log_service
from database import SessionLocal

router = APIRouter(prefix="/habits", tags=["Habit Logs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/{habit_id}/logs", response_model=schemas.HabitLogResponse, status_code=201)
def create_log(habit_id: int, log: schemas.HabitLogCreate, db: Session = Depends(get_db)):
    return log_service.create_log(db, habit_id, log.log_date, log.completed)


@router.put("/{habit_id}/logs/{log_date}", response_model=schemas.HabitLogResponse)
def update_log(habit_id: int, log_date: date, log: schemas.HabitLogUpdate, db: Session = Depends(get_db)):
    return log_service.update_log(db, habit_id, log_date, log.completed)


@router.get("/{habit_id}/logs", response_model=list[schemas.HabitLogResponse])
def get_logs(habit_id: int, db: Session = Depends(get_db)):
    return log_service.get_logs(db, habit_id)
