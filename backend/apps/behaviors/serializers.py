from rest_framework import serializers

from apps.behaviors.models import UserBehavior
from apps.resources.serializers import ResourceListSerializer
from apps.resources.models import Resource


class BrowseSerializer(serializers.Serializer):
    resource_id = serializers.IntegerField()

    def validate_resource_id(self, value):
        if not Resource.objects.filter(id=value).exists():
            raise serializers.ValidationError("资源不存在")
        return value


class BookmarkSerializer(serializers.Serializer):
    resource_id = serializers.IntegerField()

    def validate_resource_id(self, value):
        if not Resource.objects.filter(id=value).exists():
            raise serializers.ValidationError("资源不存在")
        return value


class RateSerializer(serializers.Serializer):
    resource_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)

    def validate_resource_id(self, value):
        if not Resource.objects.filter(id=value).exists():
            raise serializers.ValidationError("资源不存在")
        return value


class BehaviorResourceSerializer(serializers.ModelSerializer):
    """Flattens behavior + resource into one object for history/favorites/ratings lists."""

    resource = ResourceListSerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserBehavior
        fields = ["id", "resource", "behavior_type", "rating", "created_at"]
