from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import AppUser, UserProfile
from recipes.models import Recipe


def full_profile(user, role: str) -> UserProfile:
    return UserProfile.objects.create(
        user=user,
        role=role,
        age=28,
        height=165,
        weight=65,
        gender="male",
        activity_level="low",
        dietary_goal="lose",
    )


class RecipeDetailVisibilityTests(TestCase):
    def setUp(self):
        self.owner = AppUser.objects.create_user(
            email="standard@eatsmart.bg",
            password="recipe",
        )
        full_profile(self.owner, "standard")

    def test_public_recipes_to_anonymous(self):
        recipe = Recipe.objects.create(
            title="Tomato Soup",
            description="A public recipe.",
            preparation_time=20,
            created_by=self.owner,
            is_public=True,
        )
        url = reverse("recipes:detail", kwargs={"pk": recipe.pk})
        response = Client().get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_recipes_to_anonymous(self):
        recipe = Recipe.objects.create(
            title="Beef with vegetables",
            description="A private recipe.",
            preparation_time=45,
            created_by=self.owner,
            is_public=False,
        )
        url = reverse("recipes:detail", kwargs={"pk": recipe.pk})
        response = Client().get(url)
        self.assertEqual(response.status_code, 404)

    def test_private_recipes_when_logged_in(self):
        recipe = Recipe.objects.create(
            title="Tuna Salad",
            description="All recipes visible to logged-in users.",
            preparation_time=15,
            created_by=self.owner,
            is_public=False,
        )
        url = reverse("recipes:detail", kwargs={"pk": recipe.pk})
        client = Client()
        viewer = AppUser.objects.create_user(
            email="standard1@eatsmart.bg",
            password="standard1",
        )
        full_profile(viewer, "standard")
        client.force_login(viewer)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)


class RecipeAPITests(TestCase):
    def setUp(self):
        self.user_a = AppUser.objects.create_user(
            email="standard2@eatsmart.bg",
            password="standard2",
        )
        full_profile(self.user_a, "standard")
        self.user_b = AppUser.objects.create_user(
            email="standard6@eatsmart.bg",
            password="standard6",
        )
        full_profile(self.user_b, "standard")

        self.public_a = Recipe.objects.create(
            title="Public A",
            description="d",
            preparation_time=10,
            created_by=self.user_a,
            type="lunch",
            is_public=True,
        )
        self.private_a = Recipe.objects.create(
            title="Private A",
            description="d",
            preparation_time=12,
            created_by=self.user_a,
            type="dinner",
            is_public=False,
        )
        self.private_b = Recipe.objects.create(
            title="Private B",
            description="d",
            preparation_time=14,
            created_by=self.user_b,
            type="breakfast",
            is_public=False,
        )
        self.url = reverse("recipes_api:recipe-list")

    def test_api_recipes_public(self):
        client = APIClient()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data["results"]}
        self.assertEqual(ids, {self.public_a.pk})

    def test_api_recipes_all(self):
        client = APIClient()
        client.force_authenticate(user=self.user_a)
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = {row["id"] for row in response.data["results"]}
        self.assertEqual(
            ids,
            {self.public_a.pk, self.private_a.pk, self.private_b.pk},
        )
