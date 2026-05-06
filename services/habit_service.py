from sqlalchemy.orm import Session
from fastapi import HTTPException
import repositories.habit_repo as habit_repo
import repositories.user_repo as user_repo


def get_habits_for_user(db: Session, user_id: int):
    # Make sure user exists first
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return habit_repo.get_habits_by_user(db, user_id)


def create_habit(db: Session, name: str, target_days_per_week: int, user_id: int):
    # Make sure user exists
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate target days
    if target_days_per_week < 1 or target_days_per_week > 7:
        raise HTTPException(
            status_code=400,
            detail="target_days_per_week must be between 1 and 7"
        )

    return habit_repo.create_habit(db, name, target_days_per_week, user_id)


def delete_habit(db: Session, habit_id: int):
    habit = habit_repo.get_habit_by_id(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    habit_repo.delete_habit(db, habit)
    return {"message": f"Habit {habit_id} deleted successfully"}
