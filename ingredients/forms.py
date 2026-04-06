from django import forms
from .models import Ingredient, RecipeIngredient


class IngredientForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = ("name", "calories_per_100g", "protein_per_100g")
        labels = {
            "name": "Ingredient name",
            "calories_per_100g": "Calories (per 100 g)",
            "protein_per_100g": "Protein (per 100 g)",
        }
        help_texts = {
            "name": "Short name as it appears in recipes (max 100 characters).",
            "calories_per_100g": "Kilocalories (kcal) per 100 grams of this ingredient.",
            "protein_per_100g": "Grams of protein per 100 grams of this ingredient.",
        }
        error_messages = {
            "name": {
                "required": "Please enter the ingredient name.",
                "max_length": "Name is too long (maximum 100 characters).",
            },
            "calories_per_100g": {
                "required": "Enter calories per 100 g.",
                "invalid": "Use a valid number (decimals allowed).",
            },
            "protein_per_100g": {
                "required": "Enter protein per 100 g.",
                "invalid": "Use a valid number (decimals allowed).",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = {"class": "form-control"}
        self.fields["name"].widget = forms.TextInput(
            attrs={
                **common,
                "placeholder": "example Oats",
                "maxlength": 100,
            }
        )
        self.fields["calories_per_100g"].widget = forms.NumberInput(
            attrs={
                **common,
                "placeholder": "example 389",
                "min": 0,
                "step": "any",
            }
        )
        self.fields["protein_per_100g"].widget = forms.NumberInput(
            attrs={
                **common,
                "placeholder": "e.g. 13.2",
                "min": 0,
                "step": "any",
            }
        )

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise forms.ValidationError(
                "Name cannot be empty or only spaces.",
                code="name_blank",
            )
        return name

    def clean_calories_per_100g(self):
        value = self.cleaned_data["calories_per_100g"]
        if value <= 0:
            raise forms.ValidationError(
                "Calories per 100 g must be greater than zero.",
                code="calories_positive",
            )
        return value

    def clean_protein_per_100g(self):
        value = self.cleaned_data["protein_per_100g"]
        if value < 0:
            raise forms.ValidationError(
                "Protein per 100 g cannot be negative.",
                code="protein_non_negative",
            )
        return value


class RecipeIngredientForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "quantity")
        labels = {
            "ingredient": "Ingredient",
            "quantity": "Quantity (grams)",
        }
        help_texts = {
            "ingredient": "Choose from ingredients in the database.",
            "quantity": "Amount of this ingredient in grams (g) for this recipe.",
        }
        error_messages = {
            "ingredient": {
                "required": "Select an ingredient.",
                "invalid_choice": "Pick a valid ingredient from the list.",
            },
            "quantity": {
                "required": "Enter the quantity in grams.",
                "invalid": "Enter a valid number.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common = {"class": "form-control"}
        ing = self.fields["ingredient"]
        ing.empty_label = "Select an ingredient…"
        ing.queryset = Ingredient.objects.order_by("name")
        ing.widget.attrs.update(common)
        self.fields["quantity"].widget = forms.NumberInput(
            attrs={
                **common,
                "placeholder": "example 150",
                "min": 0,
                "step": "any",
            }
        )

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]
        if quantity <= 0:
            raise forms.ValidationError(
                "Quantity must be greater than zero grams.",
                code="quantity_positive",
            )
        return quantity
