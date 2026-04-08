from django import forms
from django.forms import inlineformset_factory
from ingredients.models import Ingredient, RecipeIngredient
from .models import Recipe


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        exclude = ("created_by", "created_at", "ingredient_items")
        help_texts = {
            "title": "Short name for this recipe (nutrition coaches maintain the catalog).",
            "type": "Breakfast, lunch, or dinner — used when matching meal plans to user targets.",
            "description": "Ingredients, steps, or notes—at least a few words.",
            "preparation_time": "Total active prep + cook time in minutes.",
            "image": "JPEG or PNG; shown on the recipe page and in the list.",
            "is_public": "If checked, other users can see this recipe in suggestions.",
        }
        labels = {
            "title": "Recipe title",
            "type": "Meal type",
            "description": "Description",
            "preparation_time": "Preparation time (minutes)",
            "image": "Photo",
            "is_public": "Public recipe",
        }
        error_messages = {
            "title": {
                "required": "Every recipe needs a title.",
                "max_length": "Title is too long (maximum 150 characters).",
            },
            "type": {
                "required": "Choose whether this is breakfast, lunch, or dinner.",
                "invalid_choice": "Pick breakfast, lunch, or dinner.",
            },
            "description": {
                "required": "Please describe how to make this recipe.",
            },
            "preparation_time": {
                "required": "Enter preparation time in minutes.",
                "invalid": "Use a whole number of minutes.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attrs = {"class": "form-control"}
        self.fields["title"].widget = forms.TextInput(
            attrs={
                **attrs,
                "placeholder": "example Protein Pancakes",
            }
        )
        self.fields["type"].widget.attrs.update(attrs)
        self.fields["description"].widget = forms.Textarea(
            attrs={
                **attrs,
                "placeholder": "Describe preparation",
                "rows": 10,
            }
        )
        self.fields["preparation_time"].widget = forms.NumberInput(
            attrs={
                **attrs,
                "placeholder": "example 25",
                "min": 1,
                "max": 10000,
                "step": 1,
            }
        )
        self.fields["image"].widget.attrs.update({"class": "form-control"})
        self.fields["image"].required = False
        self.fields["is_public"].widget.attrs.update({"class": "form-check-input"})

        if self.instance.pk:
            created = self.instance.created_at
            self.fields["created_at_display"] = forms.CharField(
                label="Created at",
                required=False,
                disabled=True,
                initial=(
                    created.strftime("%Y-%m-%d %H:%M")
                    if created
                    else "—"
                ),
                help_text="Set automatically when this recipe was first saved.",
                widget=forms.TextInput(attrs=attrs),
            )
            creator = self.instance.created_by
            self.fields["created_by_display"] = forms.CharField(
                label="Created by",
                required=False,
                disabled=True,
                initial=(creator.email if creator else "—"),
                help_text="Account that created this recipe.",
                widget=forms.TextInput(attrs=attrs),
            )
            self.field_order = [
                "created_at_display",
                "created_by_display",
                "title",
                "type",
                "description",
                "preparation_time",
                "image",
                "is_public",
            ]

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 3:
            raise forms.ValidationError(
                "Title must be at least 3 characters (not counting spaces on the ends).",
                code="title_too_short",
            )
        return title

    def clean_description(self):
        text = self.cleaned_data["description"].strip()
        if len(text) < 10:
            raise forms.ValidationError(
                "Description should be at least 10 characters so others know how to cook it.",
                code="description_too_short",
            )
        return text

    def clean_preparation_time(self):
        minutes = self.cleaned_data["preparation_time"]
        if minutes < 1:
            raise forms.ValidationError(
                "Preparation time must be at least 1 minute.",
                code="time_too_low",
            )
        if minutes > 10000:
            raise forms.ValidationError(
                "That preparation time seems too long (max 10,000 minutes / one week).",
                code="time_too_high",
            )
        return minutes


class RecipeIngredientLineForm(forms.ModelForm):

    class Meta:
        model = RecipeIngredient
        fields = ("ingredient", "quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ingredient"].required = False
        self.fields["quantity"].required = False
        self.fields["ingredient"].queryset = Ingredient.objects.order_by("name")
        self.fields["ingredient"].empty_label = "Choose food…"
        attrs = {"class": "form-control"}
        self.fields["ingredient"].widget.attrs.update(attrs)
        self.fields["quantity"].widget = forms.NumberInput(
            attrs={
                **attrs,
                "placeholder": "example 150",
                "min": 0,
                "step": "any",
            }
        )
        if "DELETE" in self.fields:
            self.fields["DELETE"].label = "Remove"
            self.fields["DELETE"].widget.attrs.update({"class": "form-check-input"})

    def clean(self):
        cleaned = super().clean()
        ing = cleaned.get("ingredient")
        qty = cleaned.get("quantity")
        if ing is None or not qty:
            return cleaned
        if ing is None or not qty:
            raise forms.ValidationError(
                "Select a ingredient and enter grams, or clear the row.",
            )
        if qty <= 0:
            raise forms.ValidationError(
                "Use a gram amount greater than zero.",
                code="quantity_positive",
            )
        return cleaned


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientLineForm,
    extra=1,
    min_num=0,
    validate_min=False,
    can_delete=True,
    max_num=300,
    validate_max=True,
)
