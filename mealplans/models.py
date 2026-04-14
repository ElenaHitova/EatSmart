from django.db import models
from accounts.models import AppUser
from recipes.models import Recipe


class MealPlan(models.Model):
    class GenerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    week_start_date = models.DateField()
    generation_status = models.CharField(
        max_length=16,
        choices=GenerationStatus.choices,
        default=GenerationStatus.DONE,
        db_index=True,
    )
    generation_notice = models.TextField(
        blank=True,
        help_text="Set by the background worker (warnings after target-based generation).",
    )
    breakfast_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meal_plans_breakfast",
    )
    lunch_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meal_plans_lunch",
    )
    dinner_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="meal_plans_dinner",
    )

    class Meta:
        ordering = ["week_start_date", "user_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "week_start_date"],
                name="mealplans_mealplan_user_week_start_unique",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} — {self.week_start_date}"
