import django_filters
from django.db.models import Q

from categories.models import Category

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(), field_name="category"
    )
    difficulty = django_filters.ChoiceFilter(
        choices=Recipe.DIFFICULTY_CHOICES, field_name="difficulty"
    )
    prep_time_max = django_filters.NumberFilter(
        field_name="prep_time", lookup_expr="lte"
    )
    cook_time_max = django_filters.NumberFilter(
        field_name="cook_time", lookup_expr="lte"
    )
    total_time_max = django_filters.NumberFilter(method="filter_total_time_max")
    servings_min = django_filters.NumberFilter(field_name="servings", lookup_expr="gte")
    servings_max = django_filters.NumberFilter(field_name="servings", lookup_expr="lte")
    is_featured = django_filters.BooleanFilter(field_name="is_featured")
    author = django_filters.CharFilter(method="filter_by_author")

    class Meta:
        model = Recipe
        fields = []

    def filter_total_time_max(self, queryset, name, value):
        """Jami vaqt bo'yicha filterlash"""
        return queryset.extra(where=["prep_time + cook_time <= %s"], params=[value])

    def filter_by_author(self, queryset, name, value):
        """Muallif nomi bo'yicha qidirish"""
        return queryset.filter(
            Q(author__first_name__icontains=value)
            | Q(author__last_name__icontains=value)
            | Q(author__email__icontains=value)
        )
