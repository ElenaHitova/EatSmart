from django.contrib import admin
from django.contrib import messages
from accounts.models import UserProfile
from nutrition.services.meal_plan_generator import generate_meal_plan
from .models import MealPlan


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "week_start_date",
        "breakfast_recipe",
        "lunch_recipe",
        "dinner_recipe",
    )
    list_filter = ("week_start_date",)
    search_fields = ("user__email",)
    autocomplete_fields = (
        "user",
        "breakfast_recipe",
        "lunch_recipe",
        "dinner_recipe",
    )
    actions = ("fill_from_profile_action",)

    @admin.action(description="Fill recipes from user profile (targets + recipe type)")
    def fill_from_profile_action(self, request, queryset):
        for plan in queryset:
            try:
                profile = UserProfile.objects.get(user=plan.user)
            except UserProfile.DoesNotExist:
                self.message_user(
                    request,
                    f"Meal plan {plan.pk}: user has no profile.",
                    level=messages.ERROR,
                )
                continue
            generate_meal_plan(profile, plan.week_start_date, meal_plan=plan)
            self.message_user(
                request,
                f"Meal plan {plan.pk}: recipes updated from targets.",
                level=messages.SUCCESS,
            )
