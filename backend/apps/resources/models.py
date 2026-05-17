from django.db import models
from django.conf import settings


class Resource(models.Model):
    class ResourceType(models.TextChoices):
        VIDEO = "video", "视频"
        ARTICLE = "article", "文章"
        EXERCISE = "exercise", "练习题"

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "初级"
        INTERMEDIATE = "intermediate", "中级"
        ADVANCED = "advanced", "高级"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    resource_type = models.CharField(max_length=20, choices=ResourceType.choices)
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.BEGINNER)
    source = models.CharField(max_length=200, blank=True, default="")
    url = models.URLField(max_length=500)
    cover_image = models.URLField(max_length=500, blank=True, default="")
    avg_rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)
    browse_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "学习资源"
        verbose_name_plural = "学习资源"

    def __str__(self):
        return self.title
