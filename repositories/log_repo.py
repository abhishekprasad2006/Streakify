from sqlalchemy.orm import Session
from datetime import date
import models


def get_log_by_habit_and_date(db: Session, habit_id: int, log_date: date):
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.log_date == log_date
    ).first()


def get_logs_by_habit(db: Session, habit_id: int):
    return db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id
    ).order_by(models.HabitLog.log_date).all()


def create_log(db: Session, habit_id: int, log_date: date, completed: bool):
    log = models.HabitLog(
        habit_id=habit_id,
        log_date=log_date,
        completed=completed
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_log(db: Session, log: models.HabitLog, completed: bool):
    log.completed = completed
    db.commit()
    db.refresh(log)
    return log
