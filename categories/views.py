import logging

from django.db.models import Count, Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category
from .serializers import CategoryListSerializer, CategorySerializer
from dishes.models import Recipe
from dishes.serializers import RecipeListSerializer


logger = logging.getLogger("categories")



class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.annotate(recipes_count=Count("recipe")).order_by("name")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategorySerializer
        return CategoryListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class CategoryRecipesView(APIView):
    """Kategoriya bo'yicha retseptlar"""

    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=404)

        recipes = Recipe.objects.filter(category=category, is_draft=False).order_by("-created_at")
        serializer = RecipeListSerializer(recipes, many=True)
        return Response(
            {"category": CategorySerializer(category).data, "recipes": serializer.data}
        )


class PopularCategoriesView(generics.ListAPIView):
    """Ommabop kategoriyalar"""

    serializer_class = CategoryListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return (
            Category.objects.annotate(
                recipes_count=Count("recipe", filter=Q(recipe__is_draft=False))
            )
            .filter(recipes_count__gt=0)
            .order_by("-recipes_count")[:10]
        )
