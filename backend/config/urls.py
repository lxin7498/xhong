from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.urls_auth")),
    path("api/users/", include("apps.users.urls")),
    path("api/", include("apps.resources.urls")),
    path("api/behaviors/", include("apps.behaviors.urls")),
    path("api/recommendations/", include("apps.recommendations.urls")),
]
