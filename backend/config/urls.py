from django.contrib import admin
from django.urls import path, include
from apps.users.urls import auth_urlpatterns, user_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include(auth_urlpatterns)),
    path("api/users/", include(user_urlpatterns)),
    path("api/resources/", include("apps.resources.urls")),
    path("api/behaviors/", include("apps.behaviors.urls")),
    path("api/recommendations/", include("apps.recommendations.urls")),
]
