from accounts.models import UserProfile
from nutrition.utils import ACTIVITY_MULTIPLIER


def calculate_bmr(profile: UserProfile):
    if profile.gender == "male":
        return 10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
    return 10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161


def calculate_daily_calories(profile: UserProfile):
    bmr = calculate_bmr(profile)
    multiplier = ACTIVITY_MULTIPLIER.get(profile.activity_level, 1.55)
    tdee = bmr * multiplier
    if profile.dietary_goal == "lose":
        return tdee - 500
    if profile.dietary_goal == "gain":
        return tdee + 500
    return tdee