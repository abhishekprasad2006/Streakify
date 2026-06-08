from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
import services.user_service as user_service
from database import SessionLocal

# Creates a router for all user-related endpoints
router = APIRouter(prefix="/users", tags=["Users"])


# Dependency function to provide a database session
def get_db():
    db = SessionLocal()  # Create a new database session
    try:
        yield db         # Give the session to the endpoint
    finally:
        db.close()       # Close the session after request completes


# POST /users
# Creates a new user
@router.post("", status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Calls service layer to create a user
    return user_service.create_user(db, user.name, user.email)


# GET /users/{user_id}/habits
# Returns all habits belonging to a user
@router.get("/{user_id}/habits", response_model=list[schemas.HabitResponse])
def get_user_habits(user_id: int, db: Session = Depends(get_db)):
    import services.habit_service as habit_service
    # Fetch habits for the given user
    return habit_service.get_habits_for_user(db, user_id)


# GET /users/{user_id}/dashboard
# Returns dashboard statistics for a user
@router.get("/{user_id}/dashboard")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    import services.dashboard_service as dashboard_service
    # Fetch dashboard data (streaks, completion stats, etc.)
    return dashboard_service.get_dashboard(db, user_id)


# GET /users/{user_id}
# Returns details of a specific user
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):  # Dependency Injection
    # Fetch user by ID
    return user_service.get_user(db, user_id)


# DELETE /users/{user_id}
# Deletes a specific user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # Delete user and return result
    return user_service.delete_user(db, user_id)