from accounts.models import UserProfile
from mealplans.models import MealPlan
from nutrition.services.calories import calculate_daily_calories
from nutrition.services.protein import calculate_daily_protein
from nutrition.services.recipe_nutrition import calculate_recipe_nutrition
from nutrition.utils import MEAL_DISTRIBUTION
from recipes.models import Recipe

RECIPE_FK_BY_MEAL_TYPE = {
    "breakfast": "breakfast_recipe_id",
    "lunch": "lunch_recipe_id",
    "dinner": "dinner_recipe_id",
}

def used_recipe_ids(user, week_start_date, meal_type):

    past_plans = MealPlan.objects.filter(user=user)
    if week_start_date is not None:
        past_plans = past_plans.exclude(week_start_date=week_start_date)
    field = RECIPE_FK_BY_MEAL_TYPE[meal_type]

    return {
        pk for pk in past_plans.values_list(field, flat=True) if pk
    }


def pick_best_recipes_for_day(profile: UserProfile, meal_plan=None, week_start_date=None):
    target_calories = calculate_daily_calories(profile)
    target_protein = calculate_daily_protein(profile)

    if week_start_date is None and meal_plan is not None:
        week_start_date = meal_plan.week_start_date

    used_this_run = set()
    result = {}

    for meal_type, ratio in MEAL_DISTRIBUTION.items():
        slot_cal = target_calories * ratio
        slot_prot = target_protein * ratio

        used_recipe = used_recipe_ids(profile.user, week_start_date, meal_type)
        unavailable_ids = used_recipe | used_this_run
        scored = []

        for recipe in Recipe.objects.filter(type=meal_type):
            nutrition = calculate_recipe_nutrition(recipe)
            if nutrition["calories"] <= 0 and nutrition["protein"] <= 0:
                continue
            diff = abs(nutrition["calories"] - slot_cal) + abs(
                nutrition["protein"] - slot_prot
            )
            scored.append((diff, recipe))
        scored.sort(key=lambda item: item[0])

        best = next(
            (recipe for _, recipe in scored if recipe.pk not in unavailable_ids),
            scored[0][1] if scored else None,
        )
        if best is not None:
            used_this_run.add(best.pk)
        result[meal_type] = best

    return result


def generate_meal_plan(profile, week_start_date,  meal_plan=None):
    picks = pick_best_recipes_for_day(
        profile, meal_plan=meal_plan, week_start_date=week_start_date
    )

    if meal_plan is None:
        meal_plan = MealPlan(
            user=profile.user,
            week_start_date=week_start_date,
            breakfast_recipe=picks["breakfast"],
            lunch_recipe=picks["lunch"],
            dinner_recipe=picks["dinner"],
        )
        meal_plan.save()
    else:
        meal_plan.breakfast_recipe = picks["breakfast"]
        meal_plan.lunch_recipe = picks["lunch"]
        meal_plan.dinner_recipe = picks["dinner"]
        meal_plan.save(update_fields=[
            "breakfast_recipe",
            "lunch_recipe",
            "dinner_recipe",
        ])
    return picks
