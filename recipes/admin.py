from django.contrib import admin
from .models import Recipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "created_by", "preparation_time", "is_public", "image", "created_at")
    list_filter = ("type", "is_public", "created_at")
    search_fields = ("title", "description", "created_by__email")
    autocomplete_fields = ("created_by",)
