from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recommendations.engine import get_recommendations, refresh_recommendations
from apps.recommendations.tasks import schedule_compute, get_status
from apps.resources.models import Resource
from apps.resources.serializers import ResourceListSerializer


def _build_response(result):
    """Resolve resource IDs returned by the engine into serialized objects."""
    id_to_resource = {
        r.id: r
        for r in Resource.objects.filter(id__in=result["items"]).prefetch_related("behaviors")
    }
    ordered = [id_to_resource[rid] for rid in result["items"] if rid in id_to_resource]
    return {
        "results": ResourceListSerializer(ordered, many=True).data,
        "cold_start": result["cold_start"],
        "count": len(ordered),
    }


class RecommendationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        task_status = get_status(user.id)

        # If computing, return whatever is cached (or cold-start fallback)
        if task_status == "computing":
            result = get_recommendations(user, refresh=False)
            data = _build_response(result)
            data["computing"] = True
            return Response(data)

        # Normal path: return cached or compute synchronously first time
        result = get_recommendations(user, refresh=False)
        return Response(_build_response(result))


class RecommendationRefreshView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Grab current results BEFORE clearing cache
        old_result = get_recommendations(user, refresh=False)

        # Fire-and-forget: schedule async recompute
        schedule_compute(user.id)

        # Clear cache so the async worker writes fresh data
        from django.core.cache import cache
        cache.delete(f"recs:{user.id}")

        data = _build_response(old_result)
        data["computing"] = True
        return Response(data, status=status.HTTP_200_OK)
