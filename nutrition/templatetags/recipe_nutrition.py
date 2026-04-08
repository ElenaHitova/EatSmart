
from django import template

from nutrition.services.recipe_nutrition import get_recipe_nutrition_summary

register = template.Library()

@register.simple_tag
def recipe_nutrition(recipe):
    nutrition = get_recipe_nutrition_summary(recipe)

    calories = nutrition["calories_kcal"]
    protein = nutrition["protein_g"]

    parts = []

    if calories > 0:
        parts.append(f"~ {calories} kcal")

    if protein > 0:
        if float(protein).is_integer():
            protein = int(protein)
        parts.append(f"{protein} g protein")

    return " · ".join(parts) if parts else "—"