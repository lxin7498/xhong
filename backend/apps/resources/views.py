from rest_framework import generics, filters
from .models import Resource
from .serializers import ResourceListSerializer, ResourceDetailSerializer
from .permissions import IsAdminOrReadOnly


class ResourceListCreateView(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "category", "tags"]
    ordering_fields = ["created_at", "browse_count", "avg_rating", "rating_count"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ResourceDetailSerializer
        return ResourceListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        return ResourceDetailSerializer
