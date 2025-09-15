from django.urls import path
from . import views

app_name = "dishes"

urlpatterns = [
    # Recipes
    path("", views.RecipeListCreateView.as_view(), name="recipe_list_create"),
    path("<slug:slug>/", views.RecipeDetailView.as_view(), name="recipe_detail"),
    path("featured/", views.FeaturedRecipesView.as_view(), name="featured_recipes"),
    path("popular/", views.PopularRecipesView.as_view(), name="popular_recipes"),

    # Ratings
    path("<slug:recipe_id>/ratings/", views.RatingListCreateView.as_view(), name="recipe_ratings"),
    path("<slug:recipe_id>/ratings/delete/", views.RatingDeleteView.as_view(), name="delete_rating"),

    # Comments
    path("<slug:recipe_id>/comments/", views.CommentListCreateView.as_view(), name="recipe_comments"),
    path("comments/<int:pk>/", views.CommentDetailView.as_view(), name="comment_detail"),
    path('', views.home, name='home'),
]
