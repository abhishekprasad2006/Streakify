from sqlalchemy.orm import Session
from fastapi import HTTPException
import repositories.user_repo as user_repo
import repositories.habit_repo as habit_repo


def get_user(db: Session, user_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Count total habits for this user
    habits = habit_repo.get_habits_by_user(db, user_id)
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at,
        "total_habits": len(habits)
    }


def create_user(db: Session, name: str, email: str):
    # Check if email is already taken
    existing = user_repo.get_user_by_email(db, email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return user_repo.create_user(db, name, email)


def delete_user(db: Session, user_id: int):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_repo.delete_user(db, user)
    return {"message": f"User {user_id} deleted successfully"}
