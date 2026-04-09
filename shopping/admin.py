from django.contrib import admin
from .models import ShoppingItem, ShoppingList


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email",)
    autocomplete_fields = ("user",)


@admin.register(ShoppingItem)
class ShoppingItemAdmin(admin.ModelAdmin):
    list_display = ("shopping_list", "ingredient", "quantity", "is_bought")
    list_filter = ("is_bought",)
    list_filter = ("ingredient",)
    search_fields = ("shopping_list__user__email", "ingredient__name")
    autocomplete_fields = ("shopping_list", "ingredient")
