import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ("easy", _("Easy")),
        ("medium", _("Medium")),
        ("hard", _("Hard")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True, blank=True)
    description = models.TextField(_("Description"))
    ingredients = models.TextField(
        _("Ingredients"), help_text=_("Each ingredient on a new line")
    )
    instructions = models.TextField(_("Instructions"))
    image = models.ImageField(
        _("Image"), upload_to="recipes/%Y/%m/%d/", null=True, blank=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Author")
    )
    category = models.ForeignKey(
        "categories.Category", on_delete=models.CASCADE, verbose_name=_("Category")
    )
    difficulty = models.CharField(
        _("Difficulty"), max_length=10, choices=DIFFICULTY_CHOICES, default="easy"
    )
    prep_time = models.PositiveIntegerField(_("Preparation time (minutes)"), default=0)
    cook_time = models.PositiveIntegerField(_("Cooking time (minutes)"), default=0)
    servings = models.PositiveIntegerField(_("Servings"), default=1)
    is_draft = models.BooleanField(_("Is draft"), default=True)
    is_featured = models.BooleanField(_("Is featured"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Recipe")
        verbose_name_plural = _("Recipes")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_draft", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def total_time(self):
        return self.prep_time + self.cook_time

    def average_rating(self):
        ratings = self.rating_set.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0

    def ratings_count(self):
        return self.rating_set.count()


class Rating(models.Model):
    recipe = models.ForeignKey(
        "dishes.Recipe", on_delete=models.CASCADE, verbose_name=_("Recipe")
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("User")
    )
    rating = models.PositiveSmallIntegerField(
        _("Rating"), validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(_("Review"), blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")
        unique_together = ("recipe", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.recipe.title} ({self.rating}/5)"


class Comment(models.Model):
    recipe = models.ForeignKey(
        "dishes.Recipe", on_delete=models.CASCADE, verbose_name=_("Recipe")
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("User")
    )
    content = models.TextField(_("Content"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Parent comment"),
    )
    is_active = models.BooleanField(_("Is active"), default=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.recipe.title}"

    def replies(self):
        return Comment.objects.filter(parent=self, is_active=True)
