from django.core.management.base import BaseCommand
from django.db.models import Avg, Count

from categories.models import Category
from dishes.models import Rating, Recipe
from users.models import User


class Command(BaseCommand):
    help = "Display recipe statistics"

    def handle(self, *args, **options):
        # General stats
        total_recipes = Recipe.objects.count()
        published_recipes = Recipe.objects.filter(is_draft=False).count()
        draft_recipes = Recipe.objects.filter(is_draft=True).count()

        self.stdout.write(self.style.SUCCESS("=== RECIPE STATISTICS ==="))
        self.stdout.write(f"Total recipes: {total_recipes}")
        self.stdout.write(f"Published: {published_recipes}")
        self.stdout.write(f"Drafts: {draft_recipes}")

        # Category stats
        self.stdout.write("\n=== CATEGORY STATISTICS ===")
        categories_with_counts = Category.objects.annotate(
            recipe_count=Count("recipe")
        ).order_by("-recipe_count")

        for category in categories_with_counts:
            self.stdout.write(f"{category.name}: {category.recipe_count} recipes")

        # User stats
        self.stdout.write("\n=== USER STATISTICS ===")
        total_users = User.objects.count()
        chefs = User.objects.filter(is_chef=True).count()
        confirmed_users = User.objects.filter(email_confirmed=True).count()

        self.stdout.write(f"Total users: {total_users}")
        self.stdout.write(f"Chefs: {chefs}")
        self.stdout.write(f"Confirmed emails: {confirmed_users}")

        # Rating stats
        self.stdout.write("\n=== RATING STATISTICS ===")
        total_ratings = Rating.objects.count()
        avg_rating = Rating.objects.aggregate(avg=Avg("rating"))["avg"]

        self.stdout.write(f"Total ratings: {total_ratings}")
        self.stdout.write(f"Average rating: {avg_rating:.2f if avg_rating else 0}")

        # Top rated recipes
        self.stdout.write("\n=== TOP RATED RECIPES ===")
        top_recipes = (
            Recipe.objects.filter(is_draft=False)
            .annotate(avg_rating=Avg("rating__rating"), rating_count=Count("rating"))
            .filter(rating_count__gte=1)
            .order_by("-avg_rating", "-rating_count")[:5]
        )

        for recipe in top_recipes:
            self.stdout.write(
                f"{recipe.title}: {recipe.avg_rating:.2f}/5 "
                f"({recipe.rating_count} ratings)"
            )
