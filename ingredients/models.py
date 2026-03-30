from django.core.validators import MinValueValidator
from django.db import models
from recipes.models import Recipe


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    calories_per_100g = models.FloatField(
        help_text="Kilocalories per 100 g.",
    )
    protein_per_100g = models.FloatField(
        help_text="Grams of protein per 100 g (0 allowed).",
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(
        help_text="Amount of this ingredient in the recipe (grams).",
    )

    class Meta:
        ordering = ["recipe_id", "ingredient__name"]

    def __str__(self):
        return f"{self.recipe_id}: {self.ingredient.name}× {self.quantity} g"

