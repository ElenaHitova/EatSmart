from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    BaseUserCreationForm,
    UserChangeForm,
)

from accounts.models import UserProfile, AppUser

User = get_user_model()


class RegisterForm(forms.Form):

    email = forms.EmailField(
        label="Email",
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address.",
        },
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        required=True,
        strip=False,
        error_messages={"required": "Password is required."},
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your password",
                "autocomplete": "new-password",
            }
        ),
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        required=True,
        strip=False,
        error_messages={"required": "Please confirm your password."},
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repeat password",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists.",
                code="duplicate_email",
            )
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("password_confirm")
        if p1 is not None and p2 is not None and p1 != p2:
            raise forms.ValidationError(
                "The two password fields do not match.",
                code="password_mismatch",
            )
        return cleaned

    def save(self):

        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]
        return User.objects.create_user(email=email, password=password)


class LoginForm(AuthenticationForm):

    def clean_username(self):
        email = self.cleaned_data["username"].strip()
        if not email:
            return email
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            raise forms.ValidationError(
                "No account is registered with this email address.",
                code="unknown_email",
            )
        return user.email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Your password",
                "autocomplete": "current-password",
            }
        )


class UserProfileForm(forms.ModelForm):

    email = forms.EmailField(
        label="Email",
        required=False,
        disabled=True,
        help_text="Your login email (read-only). To change it, contact support or use the admin site.",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = UserProfile
        fields = (
            "role",
            "age",
            "height",
            "weight",
            "gender",
            "activity_level",
            "dietary_goal",
        )
        field_order = (
            "email",
            "role",
            "age",
            "height",
            "weight",
            "gender",
            "activity_level",
            "dietary_goal",
        )
        help_texts = {
            "role": "Standard user or nutrition coach.",
            "age": "Used with height and weight for calorie estimates.",
            "height": "Height in centimeters (cm). Must be greater than 0.",
            "weight": "Weight in kilograms (kg). Must be greater than 0.",
            "gender": "Used in basal metabolic rate calculations.",
            "activity_level": "Typical activity on most days.",
            "dietary_goal": "We adjust daily calorie targets for your goal.",
        }
        labels = {
            "role": "Account type",
            "age": "Age",
            "height": "Height (cm)",
            "weight": "Weight (kg)",
            "gender": "Gender",
            "activity_level": "Activity level",
            "dietary_goal": "Dietary goal",
        }
        error_messages = {
            "role": {
                "required": "Choose your account type.",
                "invalid_choice": "Pick a valid account type.",
            },
            "age": {
                "required": "Enter your age.",
                "invalid": "Age must be a whole number.",
            },
            "height": {
                "required": "Enter your height.",
                "invalid": "Enter a valid number.",
            },
            "weight": {
                "required": "Enter your weight.",
                "invalid": "Enter a valid number.",
            },
            "gender": {
                "required": "Choose your gender.",
                "invalid_choice": "Pick a valid gender.",
            },
            "activity_level": {
                "required": "Choose your activity level.",
                "invalid_choice": "Pick a valid activity level.",
            },
            "dietary_goal": {
                "required": "Choose your dietary goal.",
                "invalid_choice": "Pick a valid dietary goal.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common = {"class": "form-control"}

        for field in ("role", "gender", "activity_level", "dietary_goal"):
            self.fields[field].widget.attrs.update(common)

        numeric_fields = {
            "age": {"placeholder": "example 32", "min": 1, "step": 1},
            "height": {"placeholder": "example 170", "min": 1, "step": 1},
            "weight": {"placeholder": "example 70", "min": 1, "step": 1},
        }

        for field, attrs in numeric_fields.items():
            self.fields[field].widget = forms.NumberInput(
                attrs={**common, **attrs}
            )

        for name, field in self.fields.items():
            if name == "email":
                continue
            field.required = True


class AppUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = AppUser
        fields = "__all__"


class AppUserAdminCreationForm(BaseUserCreationForm):

    class Meta:
        model = AppUser
        fields = (AppUser.USERNAME_FIELD,'password1','password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

