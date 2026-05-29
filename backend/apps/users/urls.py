from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, UserProfileView, PasswordChangeView

auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
]

user_urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("me/password/", PasswordChangeView.as_view(), name="user-password"),
]

urlpatterns = auth_urlpatterns + user_urlpatterns
