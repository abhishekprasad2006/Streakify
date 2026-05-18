from datetime import date, timedelta


def calculate_streak(logs):
    completed_dates = sorted(
        [log.log_date for log in logs if log.completed],
        reverse=True
    )

    if not completed_dates:
        return 0, 0

    # Current Streak
    current_streak = 0
    check_date = date.today()

    for d in completed_dates:
        if d == check_date or d == check_date - timedelta(days=1):
            current_streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    # Longest Streak
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


def calculate_consistency_score(logs, habit_created_at, target_days_per_week):
    # Total days since habit was created
    total_days = (date.today() - habit_created_at.date()).days + 1

    # How many days were expected based on target
    # e.g. target 5 days/week = 5/7 chance each day
    expected_completions = round((target_days_per_week / 7) * total_days)

    # How many were actually completed
    # Count only unique dates to avoid duplicates inflating score
    completed_dates = set(
        log.log_date for log in logs if log.completed
    )
    completed_count = len(completed_dates)

    if expected_completions <= 0:
        return 0

    score = round((completed_count / expected_completions) * 100)

    # Cap at 100
    return min(score, 100)