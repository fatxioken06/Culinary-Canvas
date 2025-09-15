from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "email",
        "get_full_name",
        "is_chef",
        "email_confirmed",
        "is_staff",
        "date_joined",
    )
    list_display_links = ("email", "get_full_name")
    list_filter = (
        "is_chef",
        "email_confirmed",
        "is_staff",
        "is_superuser",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "profile_picture")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Custom fields"),
            {
                "fields": ("is_chef", "telegram_id", "email_confirmed"),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_chef",
                ),
            },
        ),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()

    get_full_name.short_description = _("Full name")
    get_full_name.admin_order_field = "first_name"

    actions = ["make_chef", "remove_chef", "confirm_email"]

    def make_chef(self, request, queryset):
        queryset.update(is_chef=True)
        self.message_user(request, _("Selected users marked as chefs."))

    make_chef.short_description = _("Mark selected users as chefs")

    def remove_chef(self, request, queryset):
        queryset.update(is_chef=False)
        self.message_user(request, _("Chef status removed from selected users."))

    remove_chef.short_description = _("Remove chef status from selected users")

    def confirm_email(self, request, queryset):
        queryset.update(email_confirmed=True)
        self.message_user(request, _("Email confirmed for selected users."))

    confirm_email.short_description = _("Confirm email for selected users")
