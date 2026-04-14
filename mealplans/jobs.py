import logging
from django.db import transaction
from accounts.models import UserProfile
from nutrition.services.meal_plan_generator import generate_meal_plan
from .models import MealPlan

logger = logging.getLogger(__name__)


def run_meal_plan_generation(meal_plan_id: int) -> None:

    try:
        with transaction.atomic():
            plan = MealPlan.objects.select_for_update().get(pk=meal_plan_id)
            _generate_locked(plan)
    except MealPlan.DoesNotExist:
        return
    except Exception:
        logger.exception("Meal plan generation failed for pk=%s", meal_plan_id)
        MealPlan.objects.filter(pk=meal_plan_id).update(
            generation_status=MealPlan.GenerationStatus.DONE,
            generation_notice=(
                "Generation failed unexpectedly. Try opening the plan and saving again."
            ),
        )


def _generate_locked(plan: MealPlan) -> None:
    try:
        profile = UserProfile.objects.get(user=plan.user)
    except UserProfile.DoesNotExist:
        plan.generation_status = MealPlan.GenerationStatus.DONE
        plan.generation_notice = (
            "Complete your health profile (age, height, weight, activity, goal) "
            "so we can match recipes to calorie and protein targets."
        )
        plan.save(update_fields=["generation_status", "generation_notice"])
        return

    result = generate_meal_plan(
        profile, plan.week_start_date, meal_plan=plan
    )

    if not any(result.values()):
        plan.generation_status = MealPlan.GenerationStatus.DONE
        plan.generation_notice = (
            "Could not auto-select recipes: add recipes with ingredients "
            "(calories/protein) for each meal type, then try again."
        )
        plan.save(update_fields=["generation_status", "generation_notice"])
        return

    plan.generation_status = MealPlan.GenerationStatus.DONE
    plan.generation_notice = ""
    plan.save(update_fields=["generation_status", "generation_notice"])
