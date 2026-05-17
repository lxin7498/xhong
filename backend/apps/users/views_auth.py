from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.profile.nickname or user.username,
            "avatar": user.profile.avatar or "",
        }
        return data


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
