from __future__ import annotations
from django.db import transaction
from django.db.models import Sum
from ingredients.models import Ingredient, RecipeIngredient
from mealplans.models import MealPlan
from .models import ShoppingItem, ShoppingList


def collect_recipe_ids_from_meal_plans(user) -> set[int]:
    ids: set[int] = set()
    plans = MealPlan.objects.filter(user=user).values_list(
        "breakfast_recipe_id",
        "lunch_recipe_id",
        "dinner_recipe_id",
    )
    for breakfast_id, lunch_id, dinner_id in plans:
        ids.update(filter(None, [breakfast_id, lunch_id, dinner_id]))

    return ids


def aggregate_ingredient_grams(recipe_ids: set[int]) -> dict[int, float]:

    if not recipe_ids:
        return {}
    rows = (RecipeIngredient.objects.filter(recipe_id__in=recipe_ids).values("ingredient_id").annotate(total=Sum("quantity")))

    return {row["ingredient_id"]: float(row["total"])
            for row in rows}
@transaction.atomic
def regenerate_shopping_list(user) -> ShoppingList | None:

    recipe_ids = collect_recipe_ids_from_meal_plans(user)
    aggregated = aggregate_ingredient_grams(recipe_ids)
    if not aggregated:
        return latest_shopping_list(user)
    ShoppingList.objects.filter(user=user).delete()
    names = dict(
        Ingredient.objects.filter(pk__in=aggregated).values_list("pk", "name"),
    )
    sorted_ids = sorted(
        aggregated,
        key=lambda iid: (names.get(iid) or "").lower(),
    )
    sl = ShoppingList.objects.create(user=user)
    ShoppingItem.objects.bulk_create(
        [
            ShoppingItem(
                shopping_list=sl,
                ingredient_id=ing_id,
                quantity=round(aggregated[ing_id], 2),
                is_bought=False,
            )
            for ing_id in sorted_ids
        ],
    )
    return sl


def latest_shopping_list(user):
    return (
        ShoppingList.objects.filter(user=user)
        .order_by("-created_at")
        .first()
    )


@transaction.atomic
def update_bought_flags(user, bought_item_ids: set[int]) -> None:
    sl = latest_shopping_list(user)
    if sl is None:
        return
    items = list(sl.items.all())
    allowed = {item.pk for item in items}
    bought = bought_item_ids & allowed
    for item in items:
        item.is_bought = item.pk in bought
    ShoppingItem.objects.bulk_update(items, ["is_bought"])
