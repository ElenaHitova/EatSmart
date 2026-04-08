from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.roles import can_manage_food_catalog, is_standard_user
from .forms import MealPlanForm
from .models import MealPlan
from .services import apply_target_based_recipes


class MealPlanListView(LoginRequiredMixin, ListView):
    model = MealPlan
    context_object_name = "meal_plans"
    template_name = "mealplans/mealplan_list.html"
    paginate_by = 20

    def get_queryset(self):
        return (
            MealPlan.objects.filter(user=self.request.user)
            .select_related(
                "breakfast_recipe",
                "lunch_recipe",
                "dinner_recipe",
            )
            .prefetch_related(
                "breakfast_recipe__recipeingredient_set__ingredient",
                "lunch_recipe__recipeingredient_set__ingredient",
                "dinner_recipe__recipeingredient_set__ingredient",
            )
            .order_by("-week_start_date")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["is_standard_user"] = is_standard_user(u)
        ctx["can_manage_recipes"] = can_manage_food_catalog(u)
        return ctx


class MealPlanDetailView(LoginRequiredMixin, DetailView):
    model = MealPlan
    context_object_name = "meal_plan"
    template_name = "mealplans/mealplan_detail.html"

    def get_queryset(self):
        return (
            MealPlan.objects.filter(user=self.request.user)
            .select_related(
                "breakfast_recipe",
                "lunch_recipe",
                "dinner_recipe",
            )
            .prefetch_related(
                "breakfast_recipe__recipeingredient_set__ingredient",
                "lunch_recipe__recipeingredient_set__ingredient",
                "dinner_recipe__recipeingredient_set__ingredient",
            )
        )


class MealPlanCreateView(LoginRequiredMixin, CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = "mealplans/mealplan_form.html"
    success_url = reverse_lazy("mealplans:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        use_targets = form.cleaned_data.get("use_calculated_plan", False)
        form.instance.user = self.request.user
        response = super().form_valid(form)
        if use_targets:
            apply_target_based_recipes(self.request, self.object, created=True)
        else:
            messages.success(self.request, "Meal plan created.")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading"] = "New meal plan"
        ctx["submit_label"] = "Create meal plan"
        return ctx


class MealPlanUpdateView(LoginRequiredMixin, UpdateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = "mealplans/mealplan_form.html"
    success_url = reverse_lazy("mealplans:list")

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        use_targets = form.cleaned_data.get("use_calculated_plan", False)
        response = super().form_valid(form)
        if use_targets:
            apply_target_based_recipes(self.request, self.object, created=False)
        else:
            messages.success(self.request, "Meal plan updated.")
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading"] = "Edit meal plan"
        ctx["submit_label"] = "Save changes"
        return ctx


class MealPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = MealPlan
    template_name = "mealplans/mealplan_confirm_delete.html"
    success_url = reverse_lazy("mealplans:list")
    context_object_name = "meal_plan"

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Meal plan deleted.")
        return super().delete(request, *args, **kwargs)
