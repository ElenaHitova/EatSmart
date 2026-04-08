from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from accounts.roles import can_manage_food_catalog
from ingredients.models import Ingredient, RecipeIngredient
from .forms import RecipeForm, RecipeIngredientFormSet
from .models import Recipe


class RecipeListView(ListView):
    model = Recipe
    context_object_name = "recipes"
    template_name = "recipes/recipe_list.html"
    paginate_by = 20

    def get_queryset(self):
        meal_order = Case(
            When(type="breakfast", then=Value(0)),
            When(type="lunch", then=Value(1)),
            When(type="dinner", then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
        qs = (
            Recipe.objects.all()
            .select_related("created_by")
            .prefetch_related("recipeingredient_set__ingredient")
            .annotate(_meal_order=meal_order)
            .order_by("_meal_order", "-created_at")
        )
        if not self.request.user.is_authenticated:
            return qs.filter(is_public=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["can_manage_recipes"] = (
            u.is_authenticated and can_manage_food_catalog(u)
        )
        return ctx


class RecipeDetailView(DetailView):
    model = Recipe
    context_object_name = "recipe"
    template_name = "recipes/recipe_detail.html"

    def get_queryset(self):
        qs = (
            Recipe.objects.all()
            .select_related("created_by")
            .prefetch_related("recipeingredient_set__ingredient")
        )
        if not self.request.user.is_authenticated:
            return qs.filter(is_public=True)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        r = self.object
        ctx["can_manage_recipes"] = (
            u.is_authenticated and can_manage_food_catalog(u)
        )
        ctx["can_modify_recipe"] = (
            u.is_authenticated
            and (r.created_by_id == u.id or ctx["can_manage_recipes"])
        )
        return ctx


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = RecipeIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            return self._save_recipe_with_ingredients(form, formset)
        return self.render_to_response(
            self.get_context_data(form=form, ingredient_formset=formset)
        )

    def _save_recipe_with_ingredients(self, form, formset):
        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.save()
            formset.instance = self.object
            formset.save()
        messages.success(self.request, "Recipe created.")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("recipes:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        ingredient_formset = kwargs.pop("ingredient_formset", None)
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["heading"] = "Add recipe"
        ctx["submit_label"] = "Create recipe"
        ctx["can_manage_recipes"] = can_manage_food_catalog(u)
        ctx["can_modify_recipe"] = False
        ctx["ingredient_formset"] = (
            ingredient_formset
            if ingredient_formset is not None
            else RecipeIngredientFormSet()
        )
        ctx["no_ingredients_in_db"] = not Ingredient.objects.exists()
        return ctx


class RecipeUpdateView(LoginRequiredMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipes:list")

    def get_queryset(self):
        user = self.request.user
        base = Recipe.objects.prefetch_related("recipeingredient_set__ingredient")
        if can_manage_food_catalog(user):
            return base.all()
        return base.filter(created_by=user)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = RecipeIngredientFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(self.request, "Recipe updated.")
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(
            self.get_context_data(form=form, ingredient_formset=formset)
        )

    def get_context_data(self, **kwargs):
        ingredient_formset = kwargs.pop("ingredient_formset", None)
        ctx = super().get_context_data(**kwargs)
        u = self.request.user
        ctx["heading"] = "Edit recipe"
        ctx["submit_label"] = "Save changes"
        ctx["can_manage_recipes"] = can_manage_food_catalog(u)
        ctx["can_modify_recipe"] = (
            self.object.created_by_id == u.id or ctx["can_manage_recipes"]
        )
        ctx["no_ingredients_in_db"] = not Ingredient.objects.exists()
        if ingredient_formset is not None:
            ctx["ingredient_formset"] = ingredient_formset
        elif self.request.method == "POST":
            ctx["ingredient_formset"] = RecipeIngredientFormSet(
                self.request.POST, instance=self.object
            )
        else:
            ctx["ingredient_formset"] = RecipeIngredientFormSet(instance=self.object)
        return ctx


class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_confirm_delete.html"
    success_url = reverse_lazy("recipes:list")
    context_object_name = "recipe"

    def get_queryset(self):
        user = self.request.user
        if can_manage_food_catalog(user):
            return Recipe.objects.all()
        return Recipe.objects.filter(created_by=user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Recipe deleted.")
        return super().delete(request, *args, **kwargs)


def _user_can_change_recipe(user, recipe: Recipe) -> bool:
    if user.is_superuser or user.is_staff or can_manage_food_catalog(user):
        return True
    return recipe.created_by_id == user.id


class RecipeIngredientLineDeleteView(LoginRequiredMixin, DeleteView):

    model = RecipeIngredient
    template_name = "recipes/recipeingredient_confirm_delete.html"
    context_object_name = "recipe_ingredient"

    def dispatch(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, pk=kwargs["recipe_pk"])
        if not _user_can_change_recipe(request.user, recipe):
            raise PermissionDenied
        self._recipe = recipe
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            RecipeIngredient,
            pk=self.kwargs["pk"],
            recipe_id=self.kwargs["recipe_pk"],
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["recipe"] = self._recipe
        return ctx

    def get_success_url(self):
        return reverse("recipes:detail", kwargs={"pk": self.kwargs["recipe_pk"]})

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Ingredient removed from this recipe.")
        return super().delete(request, *args, **kwargs)
