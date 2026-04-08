from django import forms
from recipes.models import Recipe
from .models import MealPlan


class MealPlanForm(forms.ModelForm):

    use_calculated_plan = forms.BooleanField(
        required=False,
        initial=True,
        label="Match recipes to my calorie & protein targets",
        help_text=(
            "Uses your health profile (BMR, activity, goal) and the nutrition "
            "service to choose breakfast, lunch, and dinner from all recipes "
            "(skipping ones already on this plan when a close alternative exists). "
            "You can still pick recipes manually below; when this "
            "is checked, those choices are replaced on save."
        ),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = MealPlan
        fields = (
            "use_calculated_plan",
            "week_start_date",
            "breakfast_recipe",
            "lunch_recipe",
            "dinner_recipe",
        )
        widgets = {
            "week_start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
            ),
            "breakfast_recipe": forms.Select(attrs={"class": "form-control"}),
            "lunch_recipe": forms.Select(attrs={"class": "form-control"}),
            "dinner_recipe": forms.Select(attrs={"class": "form-control"}),
        }
        help_texts = {
            "week_start_date": "Start of the week for this plan (one plan per week).",
            "breakfast_recipe": "Optional manual pick (ignored if “Match recipes…” is checked).",
            "lunch_recipe": "Optional manual pick.",
            "dinner_recipe": "Optional manual pick.",
        }
        labels = {
            "week_start_date": "Week starting",
            "breakfast_recipe": "Breakfast",
            "lunch_recipe": "Lunch",
            "dinner_recipe": "Dinner",
        }
        error_messages = {
            "week_start_date": {
                "required": "Choose the Monday (or start day) for this plan.",
                "invalid": "Enter a valid date.",
            },
        }

    def __init__(self, *args, user=None, **kwargs):

        RECIPE_FIELDS = ("breakfast_recipe", "lunch_recipe", "dinner_recipe")
        self._user = user
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["use_calculated_plan"].initial = False
            self.fields["week_start_date"].disabled = True
            self.fields["week_start_date"].help_text = (
                "Week start is fixed for this plan. Create a new meal plan to use a different week."
            )
        if user:
            qs = Recipe.objects.all().order_by("type", "title")
            for name in RECIPE_FIELDS:
                self.fields[name].queryset = qs
                self.fields[name].required = False

    def clean_week_start_date(self):
        date = self.cleaned_data["week_start_date"]
        if self._user is None:
            return date
        qs = MealPlan.objects.filter(user=self._user, week_start_date=date)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "You already have a meal plan for that week. Edit it or pick another date.",
                code="duplicate_week",
            )
        return date
