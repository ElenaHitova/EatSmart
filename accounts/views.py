from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile
from .utils import is_health_profile_complete


class HomeView(TemplateView):
    template_name = "home.html"


class DashboardView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if not is_health_profile_complete(request.user):
            return redirect("profile_edit")
        return redirect("mealplans:list")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        ctx["profile"] = profile
        ctx["health_profile_complete"] = is_health_profile_complete(self.request.user)
        return ctx


class ProfileEditView(LoginRequiredMixin, FormView):
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("profile")

    def get_profile(self):
        return UserProfile.objects.get_or_create(user=self.request.user)[0]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.get_profile()
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        initial["email"] = self.request.user.email
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()

        messages.success(
            self.request,
            "Your profile was updated successfully.",
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.get_profile()
        ctx["health_profile_complete"] = is_health_profile_complete(self.request.user)
        return ctx


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("profile_edit")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
