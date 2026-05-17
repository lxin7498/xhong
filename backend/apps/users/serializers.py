from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, min_length=6)
    nickname = serializers.CharField(max_length=50, required=False, allow_blank=True)
    major = serializers.CharField(max_length=100, required=False, allow_blank=True)
    grade = serializers.CharField(max_length=20, required=False, allow_blank=True)
    interest_tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "nickname", "major", "grade", "interest_tags"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 6}, "email": {"required": False}}

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "两次密码不一致"})
        return attrs

    def create(self, validated_data):
        profile_updates = {
            "nickname": validated_data.pop("nickname", ""),
            "major": validated_data.pop("major", ""),
            "grade": validated_data.pop("grade", ""),
            "interest_tags": validated_data.pop("interest_tags", []),
        }
        user = User.objects.create_user(**validated_data)
        # Signal auto-creates UserProfile; update with form fields
        for attr, value in profile_updates.items():
            setattr(user.profile, attr, value)
        user.profile.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = UserProfile
        fields = ["username", "email", "nickname", "avatar", "major", "grade", "interest_tags", "created_at"]
        read_only_fields = ["created_at"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "email" in user_data:
            instance.user.email = user_data["email"]
            instance.user.save()
        return super().update(instance, validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("原密码不正确")
        return value

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
