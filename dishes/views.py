import logging

from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend as DjangoFilterFilter
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import Comment, Rating, Recipe
from .serializers import (
    CommentCreateUpdateSerializer,
    CommentSerializer,
    RatingCreateUpdateSerializer,
    RatingSerializer,
    RecipeCreateUpdateSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
)

from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger("dishes")


# -------------------- RECIPE VIEWS --------------------
class RecipeListCreateView(generics.ListCreateAPIView):
    serializer_class = RecipeListSerializer
    filter_backends = [DjangoFilterFilter, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ["title", "description", "ingredients"]
    ordering_fields = ["created_at", "title", "prep_time", "cook_time"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Recipe.objects.select_related("author", "category").annotate(
            ratings_count=Count("rating")
        )
        if not self.request.user.is_authenticated or self.request.GET.get("my_recipes") != "true":
            queryset = queryset.filter(is_draft=False)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        recipe = serializer.save()
        logger.info(f"New recipe created: {recipe.title} by {recipe.author.email}")


class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.select_related("author", "category")
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return RecipeCreateUpdateSerializer
        return RecipeDetailSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_object(self):
        obj = super().get_object()

        if obj.is_draft and (not self.request.user.is_authenticated or obj.author != self.request.user):
            from django.http import Http404
            raise Http404("Recipe not found.")

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            if obj.author != self.request.user and not self.request.user.is_staff:
                from django.core.exceptions import PermissionDenied
                logger.warning(f"User {self.request.user.email} tried to access recipe {obj.id} they don't own")
                raise PermissionDenied("You can only edit your own recipes.")

        return obj


class FeaturedRecipesView(generics.ListAPIView):
    """Featured retseptlar"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Recipe.objects.filter(is_featured=True, is_draft=False)\
            .select_related("author", "category")\
            .order_by("-created_at")[:10]


class PopularRecipesView(generics.ListAPIView):
    """Ommabop retseptlar (reyting bo'yicha)"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Recipe.objects.filter(is_draft=False)\
            .annotate(avg_rating=Avg("rating__rating"), ratings_count=Count("rating"))\
            .filter(ratings_count__gte=3)\
            .order_by("-avg_rating", "-ratings_count")[:10]


# -------------------- RATING VIEWS --------------------
class RatingListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Rating.objects.filter(recipe_id=recipe_id).select_related("user")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RatingCreateUpdateSerializer
        return RatingSerializer

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get("recipe_id")
        existing_rating = Rating.objects.filter(recipe_id=recipe_id, user=request.user).first()

        if existing_rating:
            serializer = RatingCreateUpdateSerializer(existing_rating, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            data = request.data.copy()
            data["recipe"] = recipe_id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RatingDeleteView(APIView):
    """Reytingni o'chirish"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, recipe_id):
        try:
            rating = Rating.objects.get(recipe_id=recipe_id, user=request.user)
            rating.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rating.DoesNotExist:
            return Response({"error": "Rating not found."}, status=status.HTTP_404_NOT_FOUND)


# -------------------- COMMENT VIEWS --------------------
class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        return Comment.objects.filter(recipe_id=recipe_id, is_active=True, parent=None)\
            .select_related("user").order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommentCreateUpdateSerializer
        return CommentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["recipe"] = self.kwargs.get("recipe_id")
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user and not self.request.user.is_staff:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own comments.")

def home(request):
    # Faqat "featured" bo'lgan retseptlarni olib kelamiz
    featured_recipes = Recipe.objects.filter(is_featured=True)[:6]
    return render(request, 'home.html', {
        'featured_recipes': featured_recipes,
        'now': timezone.now()
    })