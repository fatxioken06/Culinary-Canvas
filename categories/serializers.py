from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class CategoryListSerializer(serializers.ModelSerializer):
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", "icon", "recipes_count")
