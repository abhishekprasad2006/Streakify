from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date
import repositories.user_repo as user_repo
import repositories.habit_repo as habit_repo
import repositories.log_repo as log_repo
from services.streak_service import calculate_streak, calculate_consistency_score


def get_dashboard(db: Session, user_id: int):
    # Check user exists
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    habits = habit_repo.get_habits_by_user(db, user_id)
    today = date.today()

    total_habits = len(habits)
    active_habits = sum(1 for h in habits if h.is_active)
    completed_today = 0
    current_streaks = []

    for habit in habits:
        logs = log_repo.get_logs_by_habit(db, habit.id)

        # Check if completed today
        today_log = next(
            (l for l in logs if l.log_date == today and l.completed),
            None
        )
        if today_log:
            completed_today += 1

        # Calculate streaks
        current_streak, longest_streak = calculate_streak(logs)

        # Calculate consistency score for this habit
        consistency = calculate_consistency_score(logs, habit.created_at, habit.target_days_per_week)

        current_streaks.append({
            "habitName": habit.name,
            "currentStreak": current_streak,
            "longestStreak": longest_streak,
            "consistencyScore": consistency
        })

    # Overall consistency = average of all habit consistency scores
    overall_consistency = (
        round(sum(h["consistencyScore"] for h in current_streaks) / len(current_streaks))
        if current_streaks else 0
    )

    return {
        "totalHabits": total_habits,
        "activeHabits": active_habits,
        "completedToday": completed_today,
        "currentStreaks": current_streaks,
        "consistencyScore": overall_consistency
    }
