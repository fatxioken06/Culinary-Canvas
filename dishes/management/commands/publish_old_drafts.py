import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dishes.models import Recipe

logger = logging.getLogger("dishes")


class Command(BaseCommand):
    help = "Publish draft recipes that are older than specified days"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days after which drafts should be published (default: 30)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be published without actually publishing",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        # Calculate the cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find old draft recipes
        old_drafts = Recipe.objects.filter(is_draft=True, created_at__lt=cutoff_date)

        count = old_drafts.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would publish {count} draft recipes older than {days} days"
                )
            )
            for recipe in old_drafts:
                self.stdout.write(f"  - {recipe.title} (created: {recipe.created_at})")
        else:
            if count > 0:
                # Update the recipes
                old_drafts.update(is_draft=False)

                self.stdout.write(
                    self.style.SUCCESS(f"Successfully published {count} draft recipes")
                )
                logger.info(f"Published {count} old draft recipes")

                # List published recipes
                for recipe in old_drafts:
                    self.stdout.write(f"  - Published: {recipe.title}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"No draft recipes found older than {days} days")
                )
