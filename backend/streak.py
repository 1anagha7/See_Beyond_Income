# Streak Gamification logic

def calculate_new_streak(current_streak: int, status: str, completed_recovery: bool = False) -> int:
    """
    Calculates the new streak count based on current status.
    - If status is 'On Track', increment streak by 1.
    - If status is 'Behind' but they completed a recovery action today, we preserve (freeze) the streak.
    - If status is 'Behind' and they have not recovered, the streak decays by 1 (empathetic design to avoid complete reset).
    """
    if status == "On Track":
        return current_streak + 1
    elif status == "Behind":
        if completed_recovery:
            return current_streak
        return max(0, current_streak - 1)
    return current_streak
