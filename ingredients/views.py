from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from accounts.roles import can_manage_food_catalog
from recipes.models import Recipe
from .forms import IngredientForm, RecipeIngredientForm
from .mixins import CanManageIngredientsMixin, user_can_manage_ingredients
from .models import Ingredient, RecipeIngredient


class IngredientListView(LoginRequiredMixin, CanManageIngredientsMixin, ListView):
    model = Ingredient
    context_object_name = "ingredients"
    template_name = "ingredients/ingredient_list.html"
    paginate_by = 30

    def get_queryset(self):
        return Ingredient.objects.order_by("name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["can_manage_ingredients"] = user_can_manage_ingredients(self.request.user)
        return ctx


class IngredientCreateView(LoginRequiredMixin, CanManageIngredientsMixin, CreateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "ingredients/ingredient_form.html"
    success_url = reverse_lazy("ingredients:list")

    def form_valid(self, form):
        messages.success(self.request, "Ingredient created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading"] = "Add ingredient"
        ctx["submit_label"] = "Save ingredient"
        return ctx


class IngredientUpdateView(LoginRequiredMixin, CanManageIngredientsMixin, UpdateView):
    model = Ingredient
    form_class = IngredientForm
    template_name = "ingredients/ingredient_form.html"
    success_url = reverse_lazy("ingredients:list")

    def form_valid(self, form):
        messages.success(self.request, "Ingredient updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["heading"] = "Edit ingredient"
        ctx["submit_label"] = "Save changes"
        return ctx


class IngredientDeleteView(LoginRequiredMixin, CanManageIngredientsMixin, DeleteView):
    model = Ingredient
    template_name = "ingredients/ingredient_confirm_delete.html"
    context_object_name = "ingredient"
    success_url = reverse_lazy("ingredients:list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Ingredient deleted.")
        return super().delete(request, *args, **kwargs)


class RecipeIngredientCreateView(LoginRequiredMixin, CreateView):

    model = RecipeIngredient
    form_class = RecipeIngredientForm
    template_name = "ingredients/recipeingredient_form.html"

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        base = Recipe.objects.all()
        if can_manage_food_catalog(user):
            qs = base.all()
        else:
            qs = base.filter(created_by=user)
        self.recipe = get_object_or_404(qs, pk=kwargs["recipe_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.recipe = self.recipe
        ing = form.cleaned_data["ingredient"]
        messages.success(
            self.request,
            f"Added {ing.name} to the recipe.",
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("recipes:detail", kwargs={"pk": self.recipe.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recipe"] = self.recipe
        ctx["heading"] = f"Add ingredient to “{self.recipe.title}”"
        ctx["submit_label"] = "Add to recipe"
        ctx["has_ingredients"] = Ingredient.objects.exists()
        ctx["can_manage_ingredients"] = user_can_manage_ingredients(self.request.user)
        return ctx