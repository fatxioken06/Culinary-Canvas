import logging
import random

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from .redis_helper import RedisHelper

User = get_user_model()

logger = logging.getLogger("users")
redis_helper = RedisHelper()


@shared_task
def send_verification_email(user_id):
    """6 xonali verify kod yuborish"""
    try:
        user = User.objects.get(id=user_id)

        # 6 xonali raqamli kod yaratish
        verify_code = f"{random.randint(100000, 999999)}"

        # Redis ga saqlash (24 soat)
        redis_helper.set_email_verification_code(user_id=user.id, code=verify_code)

        # Email yuborish
        subject = _("Confirm your email address")
        message = _("""
        Hello {full_name},

        Please use the following verification code to confirm your email address:

        {verify_code}

        This code will expire in 2 minutes.

        Best regards,
        Culinary Canvas Team
        """).format(full_name=user.get_full_name(), verify_code=verify_code)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Verification code sent to {user.email}")
        return f"Code sent to {user.email}"

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} not found")
        return f"User {user_id} not found"
    except Exception as e:
        logger.error(f"Error sending email: {e!s}")
        return f"Error: {e!s}"


@shared_task
def send_welcome_email(user_id):
    """Xush kelibsiz xati yuborish"""
    try:
        user = User.objects.get(id=user_id)

        subject = _("Welcome to Culinary Canvas!")
        message = _("""
        Dear {full_name},

        Welcome to Culinary Canvas! Your email has been confirmed successfully.

        You can now:
        - Create and share your favorite recipes
        - Rate and comment on other recipes
        - Build your culinary profile

        Happy cooking!

        Best regards,
        Culinary Canvas Team
        """).format(full_name=user.get_full_name())

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        logger.info(f"Welcome email sent to {user.email}")
        return f"Welcome email sent to {user.email}"

    except Exception as e:
        logger.error(f"Error sending welcome email: {e!s}")
        return f"Error: {e!s}"
