from django.db.models import Case, IntegerField, Value, When
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny
from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


def recipe_api_queryset(request):

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
    if not request.user.is_authenticated:
        return qs.filter(is_public=True)
    return qs


class RecipeListAPIView(ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return recipe_api_queryset(self.request)


class RecipeDetailAPIView(RetrieveAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return recipe_api_queryset(self.request)
