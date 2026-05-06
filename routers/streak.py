from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import repositories.habit_repo as habit_repo
import repositories.log_repo as log_repo
from services.streak_service import calculate_streak
from database import SessionLocal

router = APIRouter(prefix="/habits", tags=["Streak"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{habit_id}/streak")
def get_streak(habit_id: int, db: Session = Depends(get_db)):
    habit = habit_repo.get_habit_by_id(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logs = log_repo.get_logs_by_habit(db, habit_id)
    current_streak, longest_streak = calculate_streak(logs)

    return {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }
