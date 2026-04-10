from django.urls import path

from .api_views import IngredientDetailAPIView, IngredientListCreateAPIView

app_name = "ingredients_api"

urlpatterns = [
    path("", IngredientListCreateAPIView.as_view(), name="ingredient-list"),
    path("<int:pk>/", IngredientDetailAPIView.as_view(), name="ingredient-detail"),
]
