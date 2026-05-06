from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date, timedelta
from typing import List
import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Streakify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── USERS ───────────────────────────────────────────────

@app.post("/users", response_model=schemas.UserResponse, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db.expire_all()
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ✅ specific routes BEFORE general /{user_id} route
@app.get("/users/{user_id}/habits", response_model=List[schemas.HabitResponse])
def get_user_habits(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    return habits

@app.get("/users/{user_id}/dashboard")
def get_dashboard(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    habits = db.query(models.Habit).filter(models.Habit.user_id == user_id).all()
    today = date.today()

    completed_today = 0
    current_streaks = []

    for habit in habits:
        logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit.id).all()
        today_log = next((l for l in logs if l.log_date == today and l.completed), None)
        if today_log:
            completed_today += 1

        current_streak, longest_streak = calculate_streak(logs)

        total_days = (today - habit.created_at.date()).days + 1
        completed_count = sum(1 for l in logs if l.completed)
        consistency = round((completed_count / total_days) * 100) if total_days > 0 else 0

        current_streaks.append({
            "habitName": habit.name,
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "consistencyScore": consistency
        })

    overall_consistency = (
        round(sum(h["consistencyScore"] for h in current_streaks) / len(current_streaks))
        if current_streaks else 0
    )

    return {
        "totalHabits": len(habits),
        "activeHabits": len(habits),
        "completedToday": completed_today,
        "currentStreaks": current_streaks,
        "consistencyScore": overall_consistency
    }

# ✅ general /{user_id} route AFTER specific ones
@app.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}", status_code=200)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}


# ─── HABITS ──────────────────────────────────────────────

@app.post("/habits", response_model=schemas.HabitResponse, status_code=201)
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == habit.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_habit = models.Habit(**habit.model_dump())
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit

@app.delete("/habits/{habit_id}", status_code=200)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    db.delete(habit)
    db.commit()
    return {"message": f"Habit {habit_id} deleted successfully"}


# ─── HABIT LOGS ──────────────────────────────────────────

@app.post("/habits/{habit_id}/logs", response_model=schemas.HabitLogResponse, status_code=201)
def log_habit(habit_id: int, log: schemas.HabitLogCreate, db: Session = Depends(get_db)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    if log.log_date > date.today():
        raise HTTPException(status_code=400, detail="Cannot log future dates")

    db_log = models.HabitLog(**log.model_dump(), habit_id=habit_id)
    db.add(db_log)
    try:
        db.commit()
        db.refresh(db_log)
        return db_log
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Log already exists for this date")

@app.put("/habits/{habit_id}/logs/{log_date}", response_model=schemas.HabitLogResponse)
def update_log(habit_id: int, log_date: date, log: schemas.HabitLogUpdate, db: Session = Depends(get_db)):
    db_log = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id,
        models.HabitLog.log_date == log_date
    ).first()
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found for this date")
    db_log.completed = log.completed
    db.commit()
    db.refresh(db_log)
    return db_log

@app.get("/habits/{habit_id}/logs", response_model=List[schemas.HabitLogResponse])
def get_habit_logs(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    logs = db.query(models.HabitLog).filter(
        models.HabitLog.habit_id == habit_id
    ).order_by(models.HabitLog.log_date).all()
    return logs


# ─── STREAK ──────────────────────────────────────────────

def calculate_streak(logs):
    completed_dates = sorted(
        [log.log_date for log in logs if log.completed],
        reverse=True
    )

    if not completed_dates:
        return 0, 0

    current_streak = 0
    check_date = date.today()
    for d in completed_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            current_streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    longest_streak = 1
    temp_streak = 1
    sorted_asc = sorted(completed_dates)
    for i in range(1, len(sorted_asc)):
        if sorted_asc[i] == sorted_asc[i - 1] + timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    return current_streak, longest_streak

@app.get("/habits/{habit_id}/streak")
def get_streak(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(models.Habit).filter(models.Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")

    logs = db.query(models.HabitLog).filter(models.HabitLog.habit_id == habit_id).all()
    current_streak, longest_streak = calculate_streak(logs)

    return {
        "habit_id": habit_id,
        "habit_name": habit.name,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }