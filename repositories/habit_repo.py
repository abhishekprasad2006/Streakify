from sqlalchemy.orm import Session
import models


def get_habit_by_id(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()


def get_habits_by_user(db: Session, user_id: int):
    return db.query(models.Habit).filter(models.Habit.user_id == user_id).all()


def create_habit(db: Session, name: str, target_days_per_week: int, user_id: int):
    habit = models.Habit(
        name=name,
        target_days_per_week=target_days_per_week,
        user_id=user_id,
        is_active=True       # ✅ this was missing
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


def delete_habit(db: Session, habit: models.Habit):
    db.delete(habit)
    db.commit()