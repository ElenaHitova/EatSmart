from rest_framework import serializers
from recipes.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    image_url = serializers.SerializerMethodField()
    nutrition_summary = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "type",
            "type_display",
            "preparation_time",
            "is_public",
            "image_url",
            "nutrition_summary",
        )

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def get_nutrition_summary(self, obj):
        return obj.nutrition_summary
