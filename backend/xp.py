# XP Gamification logic

XP_DAILY_ON_TRACK = 50
XP_DAILY_BEHIND = 10
XP_QUEST_COMPLETED = 500
XP_LEARNING_READ = 100
XP_PRODUCT_ADOPTED = 1000

def get_xp_for_action(action_type: str, status: str = None) -> int:
    """
    Returns XP earned for a given action.
    """
    action_type = action_type.lower()
    if action_type == "daily_check":
        if status == "On Track":
            return XP_DAILY_ON_TRACK
        return XP_DAILY_BEHIND
    elif action_type == "complete_quest":
        return XP_QUEST_COMPLETED
    elif action_type == "read_learning":
        return XP_LEARNING_READ
    elif action_type == "adopt_product":
        return XP_PRODUCT_ADOPTED
    return 0

def calculate_level(total_xp: int) -> int:
    """
    Level starts at 1 and increases by 1 for every 1000 XP accumulated.
    """
    return 1 + int(total_xp // 1000)
