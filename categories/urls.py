from django.urls import path
from . import views

app_name = "categories"

urlpatterns = [
    path("", views.CategoryListCreateView.as_view(), name="category_list_create"),
    path("<int:pk>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("<int:pk>/recipes/", views.CategoryRecipesView.as_view(), name="category_recipes"),
    path("popular/", views.PopularCategoriesView.as_view(), name="popular_categories"),
]
