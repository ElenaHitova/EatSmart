from accounts.models import UserProfile


def calculate_daily_protein(profile: UserProfile):
    if profile.dietary_goal == "gain":
        return profile.weight * 2.0
    return profile.weight * 1.6