from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import date
import repositories.log_repo as log_repo
import repositories.habit_repo as habit_repo
import repositories.user_repo as user_repo


def create_log(db: Session, habit_id: int, log_date: date, completed: bool, user_id: int = None):
    # Check habit exists
    habit = habit_repo.get_habit_by_id(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Check habit belongs to the user if user_id provided
    if user_id and habit.user_id != user_id:
        raise HTTPException(status_code=403, detail="This habit does not belong to you")

    # Business rule: cannot log future dates
    if log_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot log future dates")

    try:
        return log_repo.create_log(db, habit_id, log_date, completed)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Log already exists for this date")


def update_log(db: Session, habit_id: int, log_date: date, completed: bool):
    # Check habit exists
    habit = habit_repo.get_habit_by_id(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    # Find the log
    log = log_repo.get_log_by_habit_and_date(db, habit_id, log_date)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found for this date")

    return log_repo.update_log(db, log, completed)


def get_logs(db: Session, habit_id: int):
    # Check habit exists
    habit = habit_repo.get_habit_by_id(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    return log_repo.get_logs_by_habit(db, habit_id)
