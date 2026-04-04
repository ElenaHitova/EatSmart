from django.db import models

from accounts.models import AppUser


class Recipe(models.Model):
    RECIPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
    ]

    title = models.CharField(max_length=150)
    type = models.CharField(
        max_length=10,
        choices=RECIPE_CHOICES,
        default="lunch",
        help_text="Choose recipe for breakfast, lunch or dinner.",
    )
    description = models.TextField()
    preparation_time = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(
        upload_to="recipe_images/",
        blank=True,
        null=True,
        help_text=("Optional photo of the finished dish."),
    )
    ingredient_items = models.ManyToManyField(
        "ingredients.Ingredient",
        through="ingredients.RecipeIngredient",
        related_name="recipes",
        blank=True,
    )

    def __str__(self):
        return self.title


