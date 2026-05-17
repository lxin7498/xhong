from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    nickname = models.CharField(max_length=50, blank=True, default="")
    avatar = models.URLField(max_length=200, blank=True, default="")
    major = models.CharField(max_length=100, blank=True, default="")
    grade = models.CharField(max_length=20, blank=True, default="")
    interest_tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
