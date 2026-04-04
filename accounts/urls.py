from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from .forms import LoginForm
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=LoginForm,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("home")),
        name="logout",
    ),
]