from django.db import models as db_models
from django.db.models import Avg, OuterRef, Subquery
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from apps.behaviors.models import UserBehavior
from apps.behaviors.serializers import (
    BrowseSerializer,
    BookmarkSerializer,
    RateSerializer,
    BehaviorResourceSerializer,
)
from apps.resources.models import Resource


class BrowseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BrowseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource_id = serializer.validated_data["resource_id"]
        UserBehavior.objects.create(
            user=request.user,
            resource_id=resource_id,
            behavior_type=UserBehavior.BehaviorType.BROWSE,
        )
        Resource.objects.filter(id=resource_id).update(browse_count=db_models.F("browse_count") + 1)
        return Response({"detail": "已记录浏览"}, status=status.HTTP_201_CREATED)


class BookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookmarkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource_id = serializer.validated_data["resource_id"]

        bookmark, created = UserBehavior.objects.get_or_create(
            user=request.user,
            resource_id=resource_id,
            behavior_type=UserBehavior.BehaviorType.BOOKMARK,
        )

        if not created:
            bookmark.delete()
            return Response({"detail": "已取消收藏", "is_bookmarked": False})

        return Response({"detail": "已收藏", "is_bookmarked": True}, status=status.HTTP_201_CREATED)


class RateCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource_id = serializer.validated_data["resource_id"]
        rating = serializer.validated_data["rating"]

        behavior, created = UserBehavior.objects.update_or_create(
            user=request.user,
            resource_id=resource_id,
            behavior_type=UserBehavior.BehaviorType.RATE,
            defaults={"rating": rating},
        )

        # Recalculate cached rating stats
        stats = UserBehavior.objects.filter(
            resource_id=resource_id,
            behavior_type=UserBehavior.BehaviorType.RATE,
        ).aggregate(avg=Avg("rating"), count=db_models.Count("id"))

        Resource.objects.filter(id=resource_id).update(
            avg_rating=round(stats["avg"] or 0, 1),
            rating_count=stats["count"],
        )

        return Response(
            {"detail": "评分成功" if created else "评分已更新", "rating": rating},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class BrowseHistoryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BehaviorResourceSerializer

    def get_queryset(self):
        latest = UserBehavior.objects.filter(
            user=OuterRef("user"),
            resource=OuterRef("resource"),
            behavior_type=UserBehavior.BehaviorType.BROWSE,
        ).order_by("-created_at")

        return (
            UserBehavior.objects.filter(
                user=self.request.user,
                behavior_type=UserBehavior.BehaviorType.BROWSE,
                pk=Subquery(latest.values("pk")[:1]),
            )
            .select_related("resource")
            .order_by("-created_at")
        )


class BookmarkListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BehaviorResourceSerializer

    def get_queryset(self):
        return (
            UserBehavior.objects.filter(
                user=self.request.user,
                behavior_type=UserBehavior.BehaviorType.BOOKMARK,
            )
            .select_related("resource")
            .order_by("-created_at")
        )


class RatingListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BehaviorResourceSerializer

    def get_queryset(self):
        return (
            UserBehavior.objects.filter(
                user=self.request.user,
                behavior_type=UserBehavior.BehaviorType.RATE,
            )
            .select_related("resource")
            .order_by("-created_at")
        )
