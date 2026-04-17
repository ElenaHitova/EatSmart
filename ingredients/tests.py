from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import AppUser, UserProfile
from ingredients.models import Ingredient


def full_profile(user, role: str) -> UserProfile:
    return UserProfile.objects.create(
        user=user,
        role=role,
        age=30,
        height=170,
        weight=70,
        gender="female",
        activity_level="medium",
        dietary_goal="maintain",
    )


class IngredientAPITests(APITestCase):
    def test_anonymous(self):
        url = reverse("ingredients_api:ingredient-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_standard_user(self):
        user = AppUser.objects.create_user(
            email="standard@eatsmart.bg",
            password="standard",
        )
        full_profile(user, "standard")
        self.client.force_login(user)
        url = reverse("ingredients_api:ingredient-list")
        response = self.client.post(
            url,
            {
                "name": "Test Ingredient Std",
                "calories_per_100g": 100,
                "protein_per_100g": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_nutrition_coach(self):
        user = AppUser.objects.create_user(
            email="ncoach@eatsmart.bg",
            password="ncoach",
        )
        full_profile(user, "nutrition_coach")
        self.client.force_login(user)
        url = reverse("ingredients_api:ingredient-list")
        response = self.client.post(
            url,
            {
                "name": "Test Ingredient",
                "calories_per_100g": 120,
                "protein_per_100g": 8,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_authenticated_user(self):
        user = AppUser.objects.create_user(
            email="user@eatsmart.bg",
            password="user",
        )
        full_profile(user, "standard")
        self.client.force_login(user)
        Ingredient.objects.create(
            name="List Ingredient",
            calories_per_100g=50,
            protein_per_100g=3,
        )
        url = reverse("ingredients_api:ingredient-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
