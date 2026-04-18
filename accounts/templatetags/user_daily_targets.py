from django import template
from accounts.utils import is_health_profile_complete
from nutrition.services.calories import calculate_daily_calories
from nutrition.services.protein import calculate_daily_protein

register = template.Library()


@register.simple_tag
def user_daily_targets(user):

    if user is None or not getattr(user, "is_authenticated", False):
        return ""
    if not is_health_profile_complete(user):
        return ""

    profile = user.userprofile
    cal = calculate_daily_calories(profile)
    prot = calculate_daily_protein(profile)

    try:
        cal_int = int(round(float(cal)))
    except (TypeError, ValueError):
        return ""

    try:
        prot_num = float(prot)
    except (TypeError, ValueError):
        return ""

    prot_int = int(round(prot_num))

    parts = [f"~ {cal_int} kcal", f"{prot_int} g protein"]
    return " and ".join(parts)