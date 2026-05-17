from django.db import models
from django.conf import settings


class UserBehavior(models.Model):
    class BehaviorType(models.TextChoices):
        BROWSE = "browse", "浏览"
        BOOKMARK = "bookmark", "收藏"
        RATE = "rate", "评分"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="behaviors")
    resource = models.ForeignKey("resources.Resource", on_delete=models.CASCADE, related_name="behaviors")
    behavior_type = models.CharField(max_length=20, choices=BehaviorType.choices)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "behavior_type", "-created_at"]),
            models.Index(fields=["resource", "behavior_type"]),
        ]
