from django.urls import path
from . import views

app_name = "mealplans"

urlpatterns = [
    path("", views.MealPlanListView.as_view(), name="list"),
    path("create/", views.MealPlanCreateView.as_view(), name="create"),
    path("<int:pk>/", views.MealPlanDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.MealPlanUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.MealPlanDeleteView.as_view(), name="delete"),
]
