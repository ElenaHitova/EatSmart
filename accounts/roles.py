from accounts.models import UserProfile


def can_manage_food_catalog(user) -> bool:
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.is_staff:
        return True

    profile = getattr(user, "userprofile", None)

    return profile and profile.role == "nutrition_coach"


def is_standard_user(user) -> bool:
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.is_staff:
        return False

    profile = getattr(user, "userprofile", None)

    return not profile or profile.role != "nutrition_coach"

