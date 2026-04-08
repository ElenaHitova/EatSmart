from django.urls import path
from ingredients.views import RecipeIngredientCreateView
from . import views

app_name = "recipes"

urlpatterns = [
    path("", views.RecipeListView.as_view(), name="list"),
    path("create/", views.RecipeCreateView.as_view(), name="create"),
    path(
        "<int:recipe_pk>/ingredients/add/",
        RecipeIngredientCreateView.as_view(),
        name="ingredient_add",
    ),
    path(
        "<int:recipe_pk>/ingredients/<int:pk>/delete/",
        views.RecipeIngredientLineDeleteView.as_view(),
        name="ingredient_line_delete",
    ),
    path("<int:pk>/", views.RecipeDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.RecipeUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.RecipeDeleteView.as_view(), name="delete"),
    path("new/", views.RecipeCreateView.as_view()),
]
