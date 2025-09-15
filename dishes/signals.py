import logging
import os

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Recipe

logger = logging.getLogger("dishes")


@receiver(post_save, sender=Recipe)
def recipe_post_save(sender, instance, created, **kwargs):
    """Recipe saqlangandan keyin slug yaratish"""
    if created and not instance.slug:
        base_slug = slugify(instance.title)
        slug = base_slug
        counter = 1
        while Recipe.objects.filter(slug=slug).exclude(id=instance.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        Recipe.objects.filter(id=instance.id).update(slug=slug)
        logger.info(f"Recipe slug created: {slug} for recipe {instance.title}")


@receiver(post_delete, sender=Recipe)
def recipe_post_delete(sender, instance, **kwargs):
    """Recipe o'chirilgandan keyin media fayllarini o'chirish"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
            logger.info(f"Recipe image deleted: {instance.image.path}")
