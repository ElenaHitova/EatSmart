from django.contrib import admin

from .models import Ingredient, RecipeIngredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "calories_per_100g", "protein_per_100g")
    list_filter = ("calories_per_100g",)
    search_fields = ("name",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "quantity")
    search_fields = ("recipe__title", "ingredient__name")
    autocomplete_fields = ("recipe", "ingredient")