from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ["title", "resource_type", "category", "difficulty", "avg_rating", "browse_count", "created_at"]
    list_filter = ["resource_type", "category", "difficulty"]
    search_fields = ["title", "description", "tags"]
    readonly_fields = ["avg_rating", "rating_count", "browse_count", "created_at", "updated_at"]
    fieldsets = (
        ("基本信息", {"fields": ("title", "description", "resource_type", "category", "tags", "difficulty")}),
        ("链接与来源", {"fields": ("source", "url", "cover_image")}),
        ("统计数据", {"fields": ("avg_rating", "rating_count", "browse_count")}),
        ("其他", {"fields": ("created_by", "created_at", "updated_at")}),
    )
