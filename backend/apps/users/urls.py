from django.urls import path
from .views import UserProfileView, PasswordChangeView

urlpatterns = [
    path("me/", UserProfileView.as_view(), name="user-profile"),
    path("me/password/", PasswordChangeView.as_view(), name="user-password"),
]
