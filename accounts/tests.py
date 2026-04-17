from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from accounts.models import AppUser, UserProfile
from accounts.roles import can_manage_food_catalog, is_standard_user


class RoleLogicTests(TestCase):
    def test_role_for_anonymous(self):
        self.assertFalse(can_manage_food_catalog(AnonymousUser()))

    def test_role_for_staff(self):
        user = AppUser.objects.create_user(
            email="admin@eatsmart.bg",
            password="admin",
            is_staff=True,
        )
        self.assertTrue(can_manage_food_catalog(user))

    def test_role_for_nutrition_coach(self):
        user = AppUser.objects.create_user(
            email="ncoach@eatsmart.bg",
            password="ncoach",
        )
        UserProfile.objects.create(
            user=user,
            role="nutrition_coach",
            age=40,
            height=170,
            weight=70,
            gender="female",
            activity_level="medium",
            dietary_goal="maintain",
        )
        self.assertTrue(can_manage_food_catalog(user))

    def test_role_for_standard_user(self):
        user = AppUser.objects.create_user(
            email="standard@eatsmart.bg",
            password="standard",
        )
        UserProfile.objects.create(
            user=user,
            role="standard",
            age=28,
            height=165,
            weight=65,
            gender="male",
            activity_level="low",
            dietary_goal="lose",
        )
        self.assertFalse(can_manage_food_catalog(user))

    def test_standard_user_true(self):
        user = AppUser.objects.create_user(
            email="standard@eatsmart.bg",
            password="standard",
        )
        UserProfile.objects.create(
            user=user,
            role="standard",
            age=40,
            height=175,
            weight=80,
            gender="male",
            activity_level="high",
            dietary_goal="gain",
        )
        self.assertTrue(is_standard_user(user))

    def test_standard_user_false(self):
        user = AppUser.objects.create_user(
            email="ncoach@eatsmart.bg",
            password="ncoach",
        )
        UserProfile.objects.create(
            user=user,
            role="nutrition_coach",
            age=35,
            height=168,
            weight=72,
            gender="female",
            activity_level="medium",
            dietary_goal="maintain",
        )
        self.assertFalse(is_standard_user(user))
