from rest_framework import serializers

from categories.serializers import CategoryListSerializer
from users.serializers import UserSerializer

from .models import Comment, Rating, Recipe


class RecipeListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.IntegerField(read_only=True)
    total_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "image",
            "author",
            "author_name",
            "category",
            "category_name",
            "difficulty",
            "prep_time",
            "cook_time",
            "total_time",
            "servings",
            "average_rating",
            "ratings_count",
            "is_featured",
            "created_at",
        )

    def get_average_rating(self, obj):
        return obj.average_rating()


class RecipeDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategoryListSerializer(read_only=True)
    average_rating = serializers.SerializerMethodField()
    ratings_count = serializers.IntegerField(read_only=True)
    total_time = serializers.IntegerField(read_only=True)
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = "__all__"
        read_only_fields = ("author", "slug", "created_at", "updated_at")

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_user_rating(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            rating = Rating.objects.filter(recipe=obj, user=user).first()
            return rating.rating if rating else None
        return None


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "title",
            "description",
            "ingredients",
            "instructions",
            "image",
            "category",
            "difficulty",
            "prep_time",
            "cook_time",
            "servings",
            "is_draft",
        )

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class RatingSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Rating
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")


class RatingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ("recipe", "rating", "review")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("user", "created_at", "updated_at")

    def get_replies(self, obj):
        if obj.parent is None:  # Only get replies for parent comments
            replies = obj.replies()
            return CommentSerializer(replies, many=True, context=self.context).data
        return []


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("recipe", "content", "parent")

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
