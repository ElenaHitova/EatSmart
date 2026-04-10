from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Ingredient
from .permissions import CanManageFoodCatalogForWrite
from .serializers import IngredientSerializer


class IngredientListCreateAPIView(ListCreateAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated, CanManageFoodCatalogForWrite]

    def get_queryset(self):
        return Ingredient.objects.all()


class IngredientDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthenticated, CanManageFoodCatalogForWrite]

    def get_queryset(self):
        return Ingredient.objects.all()
