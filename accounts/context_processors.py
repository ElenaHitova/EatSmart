from accounts.roles import can_manage_food_catalog


def navigation(request):
    u = request.user
    coach = False
    if u.is_authenticated:
        coach = u.is_superuser or u.is_staff or can_manage_food_catalog(u)
    return {
        "nav_is_nutrition_coach": coach,
    }