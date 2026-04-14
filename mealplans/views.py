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
from .services import schedule_target_based_meal_plan_generation


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

class MealPlanFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def handle_generation(self, form, created=False):
        use_targets = form.cleaned_data.get("use_calculated_plan", False)

        if use_targets:
            form.instance.generation_status = MealPlan.GenerationStatus.PENDING
            form.instance.generation_notice = ""

        response = super().form_valid(form)

        if use_targets:
            mode = schedule_target_based_meal_plan_generation(self.object.pk)
            self.object.refresh_from_db()

            if mode == "queued":
                messages.info(self.request, "Meal plan is being generated...")
            elif self.object.generation_notice:
                messages.warning(self.request, self.object.generation_notice)
            else:
                messages.success(
                    self.request,
                    "Meal plan created." if created
                    else "Meal plan updated."
                )
        else:
            messages.success(
                self.request,
                "Meal plan created." if created
                else "Meal plan updated."
            )

        return response


class MealPlanCreateView(LoginRequiredMixin, MealPlanFormMixin, CreateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = "mealplans/mealplan_form.html"
    success_url = reverse_lazy("mealplans:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return self.handle_generation(form, created=True)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading"] = "New meal plan"
        ctx["submit_label"] = "Create meal plan"
        return ctx


class MealPlanUpdateView(LoginRequiredMixin, MealPlanFormMixin, UpdateView):
    model = MealPlan
    form_class = MealPlanForm
    template_name = "mealplans/mealplan_form.html"
    success_url = reverse_lazy("mealplans:list")

    def get_queryset(self):
        return MealPlan.objects.filter(user=self.request.user)

    def form_valid(self, form):
        return self.handle_generation(form, created=False)

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
