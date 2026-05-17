from django.urls import path

from apps.behaviors import views

urlpatterns = [
    path("browse/", views.BrowseCreateView.as_view(), name="behavior-browse"),
    path("bookmark/", views.BookmarkToggleView.as_view(), name="behavior-bookmark"),
    path("rate/", views.RateCreateView.as_view(), name="behavior-rate"),
    path("history/", views.BrowseHistoryView.as_view(), name="behavior-history"),
    path("favorites/", views.BookmarkListView.as_view(), name="behavior-favorites"),
    path("ratings/", views.RatingListView.as_view(), name="behavior-ratings"),
]
