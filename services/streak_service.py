from datetime import date, timedelta


def calculate_streak(logs):
    # Only keep completed logs and sort newest first
    completed_dates = sorted(
        [log.log_date for log in logs if log.completed],
        reverse=True
    )

    if not completed_dates:
        return 0, 0

    # ── Current Streak ──────────────────────────────────
    # Start from today and walk backwards day by day
    # If the log exists for that day, count it
    # Stop as soon as a day is missing
    current_streak = 0
    check_date = date.today()

    for d in completed_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            current_streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    # ── Longest Streak ───────────────────────────────────
    # Sort oldest to newest and find the longest consecutive run
    sorted_asc = sorted(completed_dates)
    longest_streak = 1
    temp_streak = 1

    for i in range(1, len(sorted_asc)):
        if sorted_asc[i] == sorted_asc[i - 1] + timedelta(days=1):
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    return current_streak, longest_streak


def calculate_consistency_score(logs, habit_created_at):
    # How many days since habit was created
    total_days = (date.today() - habit_created_at.date()).days + 1
    completed_count = sum(1 for log in logs if log.completed)

    if total_days <= 0:
        return 0

    score = round((completed_count / total_days) * 100)
    # Cap at 100 just in case
    return min(score, 100)
