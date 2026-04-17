from datetime import date
from django.test import TestCase
from accounts.models import AppUser, UserProfile
from ingredients.models import Ingredient, RecipeIngredient
from mealplans.models import MealPlan
from recipes.models import Recipe
from shopping.services import regenerate_shopping_list


def full_profile(user, role: str) -> UserProfile:
    return UserProfile.objects.create(
        user=user,
        role=role,
        age=35,
        height=170,
        weight=72,
        gender="female",
        activity_level="medium",
        dietary_goal="maintain",
    )


class ShoppingListGenerationTests(TestCase):
    def test_shopping_list(self):
        user = AppUser.objects.create_user(
            email="standard5@eatsmart.bg",
            password="standard5",
        )
        full_profile(user, "standard")

        oats = Ingredient.objects.create(
            name="Oats",
            calories_per_100g=380,
            protein_per_100g=13,
        )
        milk = Ingredient.objects.create(
            name="Milk",
            calories_per_100g=42,
            protein_per_100g=3.4,
        )
        chicken = Ingredient.objects.create(
            name="Chicken",
            calories_per_100g=165,
            protein_per_100g=31,
        )
        cheese = Ingredient.objects.create(
            name="Cheese",
            calories_per_100g=100,
            protein_per_100g=120,
        )
        breakfast = Recipe.objects.create(
            title="Oat",
            description="d",
            preparation_time=10,
            created_by=user,
            type="breakfast",
            is_public=True,
        )
        RecipeIngredient.objects.create(
            recipe=breakfast, ingredient=oats, quantity=50
        )
        RecipeIngredient.objects.create(
            recipe=breakfast, ingredient=milk, quantity=200
        )

        lunch = Recipe.objects.create(
            title="Chicken",
            description="d",
            preparation_time=20,
            created_by=user,
            type="lunch",
            is_public=True,
        )
        RecipeIngredient.objects.create(
            recipe=lunch, ingredient=chicken, quantity=150
        )
        RecipeIngredient.objects.create(
            recipe=lunch, ingredient=milk, quantity=100
        )

        dinner = Recipe.objects.create(
            title="Cheese",
            description="d",
            preparation_time=15,
            created_by=user,
            type="dinner",
            is_public=True,
        )
        RecipeIngredient.objects.create(
            recipe=dinner, ingredient=cheese, quantity=100
        )

        MealPlan.objects.create(
            user=user,
            week_start_date=date(2026, 5, 4),
            breakfast_recipe=breakfast,
            lunch_recipe=lunch,
            dinner_recipe=dinner,
        )

        sl = regenerate_shopping_list(user)
        self.assertIsNotNone(sl)
        items = {i.ingredient_id: i.quantity for i in sl.items.all()}
        self.assertEqual(items[oats.pk], 50.0)
        self.assertEqual(items[milk.pk], 300.0)
        self.assertEqual(items[chicken.pk], 150.0)
        self.assertEqual(items[cheese.pk], 100)
