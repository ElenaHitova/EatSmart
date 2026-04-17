from datetime import date
from django.test import Client, TestCase
from django.urls import reverse
from accounts.models import AppUser, UserProfile
from mealplans.models import MealPlan
from nutrition.services.meal_plan_generator import pick_best_recipes_for_day
from nutrition.services.recipe_nutrition import calculate_recipe_nutrition
from nutrition.utils import MEAL_DISTRIBUTION
from nutrition.services.calories import calculate_daily_calories
from nutrition.services.protein import calculate_daily_protein
from ingredients.models import Ingredient, RecipeIngredient
from recipes.models import Recipe


def full_profile(user, role: str) -> UserProfile:
    return UserProfile.objects.create(
        user=user,
        role=role,
        age=32,
        height=172,
        weight=68,
        gender="female",
        activity_level="high",
        dietary_goal="maintain",
    )


class MealPlanOwnershipTests(TestCase):
    def test_user_edit_meal_plan(self):
        owner = AppUser.objects.create_user(
            email="standard1@eatsmart.bg",
            password="standard1",
        )
        full_profile(owner, "standard")
        other = AppUser.objects.create_user(
            email="standard2@eatsmart.bg",
            password="standard2",
        )
        full_profile(other, "standard")

        plan = MealPlan.objects.create(
            user=owner,
            week_start_date=date(2026, 4, 13),
        )
        url = reverse("mealplans:update", kwargs={"pk": plan.pk})

        client = Client()
        client.force_login(other)
        response = client.get(url)
        self.assertEqual(response.status_code, 404)


class MealPlanGeneratorTests(TestCase):
    def test_pick_best_recipes(self):
        user = AppUser.objects.create_user(
            email="standard3@eatsmart.bg",
            password="standard3",
        )
        profile = full_profile(user, "standard")

        target_cal = calculate_daily_calories(profile)
        target_prot = calculate_daily_protein(profile)
        owner = user

        for meal_type in ("breakfast", "lunch", "dinner"):
            ratio = MEAL_DISTRIBUTION[meal_type]
            slot_cal = target_cal * ratio
            slot_prot = target_prot * ratio
            ing = Ingredient.objects.create(
                name=f"Ideal {meal_type}",
                calories_per_100g=slot_cal,
                protein_per_100g=slot_prot,
            )
            recipe = Recipe.objects.create(
                title=f"Ideal {meal_type} recipe",
                description="d",
                preparation_time=10,
                created_by=owner,
                type=meal_type,
                is_public=True,
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ing, quantity=100
            )

        picks = pick_best_recipes_for_day(profile, week_start_date=date(2026, 4, 20))
        self.assertIsNotNone(picks["breakfast"])
        self.assertIsNotNone(picks["lunch"])
        self.assertIsNotNone(picks["dinner"])
        ids = {
            picks["breakfast"].pk,
            picks["lunch"].pk,
            picks["dinner"].pk,
        }
        self.assertEqual(len(ids), 3)

    def test_pick_best_total_calories(self):
        user = AppUser.objects.create_user(
            email="standard4@eatsmart.bg",
            password="standard4",
        )
        profile = full_profile(user, "standard")

        target_cal = calculate_daily_calories(profile)
        target_prot = calculate_daily_protein(profile)
        owner = user

        for meal_type in ("breakfast", "lunch", "dinner"):
            ratio = MEAL_DISTRIBUTION[meal_type]
            slot_cal = target_cal * ratio
            slot_prot = target_prot * ratio
            ing = Ingredient.objects.create(
                name=f"Slot {meal_type}",
                calories_per_100g=slot_cal,
                protein_per_100g=slot_prot,
            )
            recipe = Recipe.objects.create(
                title=f"Slot {meal_type} recipe",
                description="d",
                preparation_time=10,
                created_by=owner,
                type=meal_type,
                is_public=True,
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ing, quantity=100
            )

        picks = pick_best_recipes_for_day(profile, week_start_date=date(2026, 4, 27))
        total_cal = sum(
            calculate_recipe_nutrition(picks[m])["calories"]
            for m in ("breakfast", "lunch", "dinner")
        )
        total_prot = sum(
            calculate_recipe_nutrition(picks[m])["protein"]
            for m in ("breakfast", "lunch", "dinner")
        )
        self.assertAlmostEqual(total_cal, target_cal, delta=1.0)
        self.assertAlmostEqual(total_prot, target_prot, delta=1.0)
