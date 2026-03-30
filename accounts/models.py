from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):

    ACTIVITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    GOAL_CHOICES = [
        ('lose', 'Lose Weight'),
        ('maintain', 'Maintain'),
        ('gain', 'Gain Muscle'),
    ]

    GENDER_CHOICES = [
        ('female', 'Female'),
        ('male', 'Male'),
    ]

    ROLE_CHOICES = [
        ("standard", "Standard user"),
        ("nutrition_coach", "Nutrition coach"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        help_text="Standard user: meal plans from targets. Nutrition coach: also manages ingredients and recipes.",
    )
    age = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        help_text=("Full age helps in sensitive calculation of meal-plan ranges."),
    )
    height = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=("Height in centimeters (cm); must be greater than zero."),
    )
    weight = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        help_text=("Weight in kilograms (kg); must be greater than zero."),
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )
    activity_level = models.CharField(
        max_length=10,
        choices=ACTIVITY_CHOICES,
        blank=True,
        null=True,
    )
    dietary_goal = models.CharField(
        max_length=10,
        choices=GOAL_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.email} ({self.get_role_display()})"

