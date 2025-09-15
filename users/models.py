from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager  # <-- qo'shing

class User(AbstractUser):
    username = None
    email = models.EmailField(_("Email address"), unique=True)
    first_name = models.CharField(_("First name"), max_length=150)
    last_name = models.CharField(_("Last name"), max_length=150)
    is_chef = models.BooleanField(_("Is chef"), default=False)
    profile_picture = models.ImageField(
        _("Profile picture"),
        upload_to="profiles/%Y/%m/%d/",
        null=True,
        blank=True,
        help_text=_("Upload your profile picture"),
        default="static/image.png"
    )
    telegram_id = models.BigIntegerField(
        _("Telegram ID"),
        null=True,
        blank=True,
        help_text=_("Telegram user ID for bot integration"),
    )
    email_confirmed = models.BooleanField(_("Email confirmed"), default=False)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    objects = CustomUserManager()  # <-- managerni ulash

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
