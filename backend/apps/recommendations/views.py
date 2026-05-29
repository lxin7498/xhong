from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.recommendations.engine import get_recommendations, refresh_recommendations
from apps.recommendations.tasks import schedule_compute, get_status
from apps.recommendations.evaluation import get_cached_evaluation, run_evaluation
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


class MetricsView(APIView):
    """公开端点：返回离线评估指标对比数据，供前端仪表盘使用"""
    permission_classes = [AllowAny]

    def get(self, request):
        pop, cf = get_cached_evaluation()
        return self._build_response(pop, cf)

    def post(self, request):
        """强制重新运行评估（清除缓存）"""
        from django.core.cache import cache
        cache.delete("recs:eval:result")
        pop, cf = run_evaluation()
        return Response(self._build_response(pop, cf).data)

    @staticmethod
    def _build_response(pop, cf):
        def _metric_dict(result):
            return {
                "precision_5": result.precision_5,
                "recall_5": result.recall_5,
                "ndcg_5": result.ndcg_5,
                "precision_9": result.precision_9,
                "recall_9": result.recall_9,
                "ndcg_9": result.ndcg_9,
                "coverage": result.coverage,
                "rmse": result.rmse,
                "cold_start_hit_rate": result.cold_start_hit_rate,
                "cold_start_count": result.cold_start_count,
                "cold_start_hit_count": result.cold_start_hit_count,
                "total_users": result.total_users,
                "evaluable_users": result.evaluable_users,
            }

        return Response({
            "popularity": _metric_dict(pop),
            "cf": _metric_dict(cf),
            "cold_start_threshold": 5,
            "relevance_threshold": 4,
            "k_values": [5, 9],
        })
