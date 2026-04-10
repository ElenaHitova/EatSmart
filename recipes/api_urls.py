from django.urls import path
from recipes.api_views import RecipeListAPIView, RecipeDetailAPIView

app_name = "recipes_api"

urlpatterns = [
    path("", RecipeListAPIView.as_view(), name="recipe-list"),
    path("<int:pk>/", RecipeDetailAPIView.as_view(), name="recipe-detail"),
]
