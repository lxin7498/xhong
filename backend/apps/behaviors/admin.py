from django.contrib import admin

from apps.behaviors.models import UserBehavior


@admin.register(UserBehavior)
class UserBehaviorAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "resource", "behavior_type", "rating", "created_at"]
    list_filter = ["behavior_type", "created_at"]
    search_fields = ["user__username", "resource__title"]
    readonly_fields = ["created_at"]
