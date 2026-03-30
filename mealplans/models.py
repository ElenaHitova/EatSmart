from django.contrib.auth.models import User
from django.db import models

from recipes.models import Recipe


class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()

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
