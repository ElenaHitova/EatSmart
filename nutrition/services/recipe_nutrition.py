from recipes.models import Recipe


def calculate_recipe_nutrition(recipe: Recipe):
    total_calories = 0.0
    total_protein = 0.0

    for item in recipe.recipeingredient_set.all():
        factor = item.quantity / 100.0
        total_calories += item.ingredient.calories_per_100g * factor
        total_protein += item.ingredient.protein_per_100g * factor
    return {
            "calories": total_calories,
            "protein": total_protein,
    }


def get_recipe_nutrition_summary(recipe: Recipe) -> dict | None:
    raw = calculate_recipe_nutrition(recipe)
    if raw["calories"] <= 0 and raw["protein"] <= 0:
        return None
    cal_i = max(0, int(round(raw["calories"])))
    pr = round(raw["protein"], 1)
    protein_g = int(pr) if float(pr).is_integer() else pr
    return {"calories_kcal": cal_i, "protein_g": protein_g}
