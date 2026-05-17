from django.urls import path
from . import views

urlpatterns = [
    path("resources/", views.ResourceListCreateView.as_view(), name="resource-list"),
    path("resources/<int:pk>/", views.ResourceDetailView.as_view(), name="resource-detail"),
]
