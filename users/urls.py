from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

app_name = "users"

urlpatterns = [
    # ===================== Authentication =====================
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", views.RegisterView.as_view(), name="register"),

    # ===================== Email Confirmation =====================
    path(
        "confirm-email/",
        views.VerifyEmailView.as_view(),
        name="confirmation-email",
    ),
    

    # ===================== Profile =====================
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.PasswordChangeView.as_view(), name="change-password"),

    # ===================== User Data =====================
    path("my-recipes/", views.UserRecipesView.as_view(), name="user-recipes"),
    path("stats/", views.UserStatsView.as_view(), name="user-stats"),
]
