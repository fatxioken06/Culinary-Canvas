import logging
from django.db.models import Avg
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from rest_framework.parsers import MultiPartParser, FormParser

from users.redis_helper import RedisHelper

from .models import User
from .serializers import (
    PasswordChangeSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    VerifyEmailSerializer,
    UserStatsSerializer,
)
from .tasks import send_verification_email, send_welcome_email


logger = logging.getLogger("users")

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]  # <- bu qo'shildi

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_verification_email.delay(user.id)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Registration successful. Check your email for confirmation.",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserProfileUpdateSerializer
        return UserSerializer


class PasswordChangeView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            logger.info(f"Password changed for user: {user.email}")
            return Response({"message": _("Password changed successfully.")})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ====================== Class-Based Versions of FBVs ======================

from dishes.models import Recipe, Rating
from dishes.serializers import RecipeListSerializer


class UserRecipesView(generics.ListAPIView):
    """Foydalanuvchining barcha retseptlari"""
    serializer_class = RecipeListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by("-created_at")


class UserStatsView(APIView):
    """Foydalanuvchi statistikasi"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserStatsSerializer

    def get(self, request):
        user = request.user
        recipes_count = Recipe.objects.filter(author=user).count()
        published_count = Recipe.objects.filter(author=user, is_draft=False).count()
        avg_rating = (
            Rating.objects.filter(recipe__author=user).aggregate(avg_rating=Avg("rating"))[
                "avg_rating"
            ]
            or 0
        )

        return Response(
            {
                "recipes_count": recipes_count,
                "published_count": published_count,
                "draft_count": recipes_count - published_count,
                "average_rating": round(avg_rating, 2),
            }
        )

redis_helper = RedisHelper()
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyEmailSerializer
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        code = serializer.validated_data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            if user.email_confirmed:
                return Response({"message": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)
            
            # RedisHelper dan foydalanish
            cached_code = redis_helper.get_email_verification_code(user.id)

            if cached_code and cached_code == code:
                user.email_confirmed = True
                user.save()
                send_welcome_email.delay(user.id)
                return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)