from django.contrib import messages
from accounts.models import UserProfile
from nutrition.services.meal_plan_generator import generate_meal_plan
from .models import MealPlan


def apply_target_based_recipes(request, meal_plan: MealPlan, *, created: bool) -> None:
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.warning(
            request,
            "Saved your meal plan. Complete your health profile (age, height, weight, "
            "activity, goal) so we can match recipes to calorie and protein targets.",
        )
        return

    result = generate_meal_plan(
        profile, meal_plan.week_start_date, meal_plan=meal_plan
    )
    if not any(result.values()):
        messages.warning(
            request,
            "Could not auto-select recipes: add recipes with ingredients "
            "(calories/protein) for each meal type, then try again.",
        )
        return
    if created:
        messages.success(
            request,
            "Meal plan created. Breakfast, lunch, and dinner were chosen using your "
            "daily calorie and protein targets.",
        )
    else:
        messages.success(
            request,
            "Meal plan updated. Recipes were refreshed from your targets.",
        )
