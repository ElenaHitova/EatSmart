from django.test import TestCase
from accounts.models import AppUser, UserProfile
from ingredients.models import Ingredient, RecipeIngredient
from nutrition.services.calories import calculate_daily_calories
from nutrition.services.protein import calculate_daily_protein
from nutrition.services.recipe_nutrition import calculate_recipe_nutrition
from recipes.models import Recipe


class RecipeNutritionCalculationTests(TestCase):
    def test_recipe_calories(self):
        owner = AppUser.objects.create_user(
            email="user@eatsmart.bg",
            password="user",
        )
        recipe = Recipe.objects.create(
            title="Calories Test",
            description="d",
            preparation_time=10,
            created_by=owner,
            type="lunch",
        )
        ing_a = Ingredient.objects.create(
            name="Ing A",
            calories_per_100g=200,
            protein_per_100g=10,
        )
        ing_b = Ingredient.objects.create(
            name="Ing B",
            calories_per_100g=50,
            protein_per_100g=5,
        )
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing_a, quantity=100)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing_b, quantity=50)

        totals = calculate_recipe_nutrition(recipe)
        self.assertAlmostEqual(totals["calories"], 225.0)

    def test_recipe_protein(self):
        owner = AppUser.objects.create_user(
            email="user2@eatsmart.bg",
            password="user",
        )
        recipe = Recipe.objects.create(
            title="Protein Test",
            description="d",
            preparation_time=10,
            created_by=owner,
            type="dinner",
        )
        ing = Ingredient.objects.create(
            name="Ing P",
            calories_per_100g=0,
            protein_per_100g=12,
        )
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=250)

        totals = calculate_recipe_nutrition(recipe)
        self.assertAlmostEqual(totals["protein"], 30.0)
        self.assertAlmostEqual(totals["calories"], 0.0)

    def test_recipe_total(self):
        owner = AppUser.objects.create_user(
            email="user@eatsmart.bg",
            password="user",
        )
        recipe = Recipe.objects.create(
            title="Recipe Test",
            description="d",
            preparation_time=12,
            created_by=owner,
            type="breakfast",
        )
        ing_a = Ingredient.objects.create(
            name="Ing A",
            calories_per_100g=100,
            protein_per_100g=8,
        )
        ing_b = Ingredient.objects.create(
            name="Ing B",
            calories_per_100g=40,
            protein_per_100g=2,
        )
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing_a, quantity=150)
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ing_b, quantity=200)

        totals = calculate_recipe_nutrition(recipe)
        self.assertAlmostEqual(totals["calories"], 230.0)
        self.assertAlmostEqual(totals["protein"], 16.0)


class UserTargetNutritionTests(TestCase):
    def test_daily_targets(self):
        user = AppUser.objects.create_user(
            email="user@eatsmart.bg",
            password="user",
        )
        profile = UserProfile.objects.create(
            user=user,
            role="standard",
            age=30,
            weight=70,
            height=175,
            gender="male",
            activity_level="medium",
            dietary_goal="lose",
        )
        # BMR = 10*70 + 6.25*175 - 5*30 + 5 = 1648.75; TDEE = (1648.75*1.55)- 500 = 2055.5625
        self.assertAlmostEqual(calculate_daily_calories(profile), 2055.5625)
        self.assertAlmostEqual(calculate_daily_protein(profile), 112.0)
