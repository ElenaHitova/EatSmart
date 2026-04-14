def schedule_target_based_meal_plan_generation(meal_plan_id: int) -> str:
    from django.conf import settings
    from django_rq import get_queue
    from .jobs import run_meal_plan_generation

    if getattr(settings, "RQ_SYNCHRONOUS_FALLBACK", False):
        run_meal_plan_generation(meal_plan_id)
        return "inline"

    get_queue("default").enqueue(run_meal_plan_generation, meal_plan_id)
    return "queued"
