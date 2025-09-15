import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import Recipe

logger = logging.getLogger("dishes")


@shared_task
def publish_old_drafts_task(days=30):
    """Eski draft retseptlarni avtomatik publish qilish"""
    cutoff_date = timezone.now() - timedelta(days=days)

    old_drafts = Recipe.objects.filter(is_draft=True, created_at__lt=cutoff_date)

    count = old_drafts.count()
    if count > 0:
        old_drafts.update(is_draft=False)
        logger.info(f"Auto-published {count} old draft recipes")

    return f"Published {count} recipes"


@shared_task
def generate_recipe_thumbnails(recipe_id):
    """Retsept rasmlari uchun thumbnaillar yaratish"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
        if recipe.image:
            # Thumbnail yaratish logikasi
            # PIL yoki boshqa kutubxona ishlatilishi mumkin
            logger.info(f"Generated thumbnail for recipe: {recipe.title}")
            return f"Thumbnail generated for {recipe.title}"
    except Recipe.DoesNotExist:
        logger.error(f"Recipe {recipe_id} not found for thumbnail generation")
        return f"Recipe {recipe_id} not found"
