from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment, Rating, Recipe


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("user", "rating", "review", "created_at")


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("created_at",)
    fields = ("user", "content", "is_active", "created_at")


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "difficulty",
        "average_rating",
        "ratings_count",
        "is_draft",
        "is_featured",
        "created_at",
    )
    list_display_links = ("title",)
    list_filter = (
        "category",
        "difficulty",
        "is_draft",
        "is_featured",
        "created_at",
        "author__is_chef",
    )
    search_fields = (
        "title",
        "description",
        "author__email",
        "author__first_name",
        "author__last_name",
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "average_rating", "ratings_count")
    inlines = [RatingInline, CommentInline]

    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "category")}),
        (
            _("Content"),
            {"fields": ("description", "ingredients", "instructions", "image")},
        ),
        (
            _("Details"),
            {"fields": ("difficulty", "prep_time", "cook_time", "servings")},
        ),
        (_("Status"), {"fields": ("is_draft", "is_featured")}),
        (_("Statistics"), {"fields": ("average_rating", "ratings_count")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    actions = ["make_featured", "remove_featured", "publish_recipes", "make_draft"]

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, _("Selected recipes marked as featured."))

    make_featured.short_description = _("Mark selected recipes as featured")

    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, _("Featured status removed from selected recipes."))

    remove_featured.short_description = _("Remove featured status")

    def publish_recipes(self, request, queryset):
        queryset.update(is_draft=False)
        self.message_user(request, _("Selected recipes published."))

    publish_recipes.short_description = _("Publish selected recipes")

    def make_draft(self, request, queryset):
        queryset.update(is_draft=True)
        self.message_user(request, _("Selected recipes marked as draft."))

    make_draft.short_description = _("Mark selected recipes as draft")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("recipe__title", "user__email", "review")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("recipe__title", "user__email", "content")
    readonly_fields = ("created_at", "updated_at")

    actions = ["approve_comments", "reject_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, _("Selected comments approved."))

    approve_comments.short_description = _("Approve selected comments")

    def reject_comments(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, _("Selected comments rejected."))

    reject_comments.short_description = _("Reject selected comments")
