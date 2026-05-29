from django.urls import path

from apps.recommendations.views import RecommendationListView, RecommendationRefreshView, MetricsView

urlpatterns = [
    path("", RecommendationListView.as_view(), name="recommendation-list"),
    path("refresh/", RecommendationRefreshView.as_view(), name="recommendation-refresh"),
    path("metrics/", MetricsView.as_view(), name="recommendation-metrics"),
]
