from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
import services.user_service as user_service
from database import SessionLocal

router = APIRouter(prefix="/users", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user.name, user.email)


@router.get("/{user_id}/habits", response_model=list[schemas.HabitResponse])
def get_user_habits(user_id: int, db: Session = Depends(get_db)):
    import services.habit_service as habit_service
    return habit_service.get_habits_for_user(db, user_id)


@router.get("/{user_id}/dashboard")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    import services.dashboard_service as dashboard_service
    return dashboard_service.get_dashboard(db, user_id)


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.delete_user(db, user_id)
