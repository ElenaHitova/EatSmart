from django.db import models

from accounts.models import AppUser
from ingredients.models import Ingredient


class ShoppingList(models.Model):

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.email} — {self.created_at.date()}"


class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(
        ShoppingList,
        on_delete=models.CASCADE,
        related_name="items",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
    )
    quantity = models.FloatField(
        help_text="Total grams needed (summed across all recipes in your meal plans).",
    )
    is_bought = models.BooleanField(default=False)

    class Meta:
        ordering = ["shopping_list_id", "id"]

    def __str__(self):
        return f"{self.ingredient.name} × {self.quantity}"

