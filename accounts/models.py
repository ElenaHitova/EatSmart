from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User, AbstractUser


class AppUserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractUser):

    username = None
    email = models.EmailField(("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = AppUserManager()

    class Meta:
        verbose_name = ("user")
        verbose_name_plural = ("users")

    def __str__(self):
        return self.email


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

    user = models.OneToOneField(
        AppUser,
        on_delete=models.CASCADE,
        related_name="userprofile",
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        blank=True,
        null=True,
        help_text="Standard user: meal plans from targets. Nutrition coach: also manages ingredients and recipes.",
    )
    age = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        blank=True,
        null=True,
        help_text=("Age in full years (validated for sensible meal-plan ranges)."),
    )
    height = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=("Height in centimeters (cm); must be greater than zero."),
        blank=True,
        null=True,
    )
    weight = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text=("Weight in kilograms (kg); must be greater than zero."),
        blank=True,
        null=True,
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
        return f"{self.user.email} ({self.get_role_display() or 'no role'})"

