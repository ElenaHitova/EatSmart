from django.urls import path
from . import views

app_name = "ingredients"

urlpatterns = [
    path("", views.IngredientListView.as_view(), name="list"),
    path("create/", views.IngredientCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.IngredientUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.IngredientDeleteView.as_view(), name="delete"),
]
