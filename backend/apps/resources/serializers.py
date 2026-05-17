from rest_framework import serializers
from .models import Resource


class ResourceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = [
            "id", "title", "description", "resource_type", "category",
            "tags", "difficulty", "source", "cover_image",
            "avg_rating", "rating_count", "browse_count", "created_at",
        ]


class ResourceDetailSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    user_rating = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = [
            "id", "title", "description", "resource_type", "category",
            "tags", "difficulty", "source", "url", "cover_image",
            "avg_rating", "rating_count", "browse_count",
            "created_by", "created_by_name", "created_at", "updated_at",
            "user_rating", "is_bookmarked",
        ]
        read_only_fields = [
            "avg_rating", "rating_count", "browse_count", "created_by", "created_at", "updated_at",
        ]

    def _get_behaviors(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return {}
        behaviors = obj.behaviors.filter(user=request.user)
        return {b.behavior_type: b for b in behaviors}

    def get_user_rating(self, obj):
        b = self._get_behaviors(obj).get("rate")
        return b.rating if b else None

    def get_is_bookmarked(self, obj):
        return "bookmark" in self._get_behaviors(obj)
