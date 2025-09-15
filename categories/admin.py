from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "recipes_count", "get_icon", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at", "recipes_count")
    ordering = ("name",)

    fieldsets = (
        (None, {"fields": ("name", "description", "icon")}),
        (_("Statistics"), {"fields": ("recipes_count",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    def get_icon(self, obj):
        if obj.icon:
            return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
        return "-"

    get_icon.short_description = _("Icon")
