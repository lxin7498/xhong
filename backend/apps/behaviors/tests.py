from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.resources.models import Resource
from apps.behaviors.models import UserBehavior

User = get_user_model()


class BehaviorModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.resource = Resource.objects.create(
            title="R", resource_type="video", category="CS", url="http://a.com",
        )

    def test_create_browse(self):
        b = UserBehavior.objects.create(user=self.user, resource=self.resource, behavior_type="browse")
        self.assertEqual(b.behavior_type, "browse")

    def test_create_rate(self):
        b = UserBehavior.objects.create(user=self.user, resource=self.resource, behavior_type="rate", rating=4)
        self.assertEqual(b.rating, 4)


class BrowseAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass")
        self.resource = Resource.objects.create(
            title="R", resource_type="video", category="CS", url="http://a.com",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_browse(self):
        resp = self.client.post("/api/behaviors/browse/", {"resource_id": self.resource.id})
        self.assertEqual(resp.status_code, 201)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.browse_count, 1)

    def test_create_browse_unauthenticated(self):
        self.client.force_authenticate(user=None)
        resp = self.client.post("/api/behaviors/browse/", {"resource_id": self.resource.id})
        self.assertEqual(resp.status_code, 401)

    def test_browse_history(self):
        UserBehavior.objects.create(user=self.user, resource=self.resource, behavior_type="browse")
        resp = self.client.get("/api/behaviors/history/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)


class BookmarkAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass")
        self.resource = Resource.objects.create(
            title="R", resource_type="video", category="CS", url="http://a.com",
        )
        self.client.force_authenticate(user=self.user)

    def test_bookmark_toggle_create(self):
        resp = self.client.post("/api/behaviors/bookmark/", {"resource_id": self.resource.id})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data["is_bookmarked"])

    def test_bookmark_toggle_delete(self):
        self.client.post("/api/behaviors/bookmark/", {"resource_id": self.resource.id})
        resp = self.client.post("/api/behaviors/bookmark/", {"resource_id": self.resource.id})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.data["is_bookmarked"])

    def test_bookmark_list(self):
        UserBehavior.objects.create(user=self.user, resource=self.resource, behavior_type="bookmark")
        resp = self.client.get("/api/behaviors/favorites/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)


class RateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="pass")
        self.resource = Resource.objects.create(
            title="R", resource_type="video", category="CS", url="http://a.com",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_rate(self):
        resp = self.client.post("/api/behaviors/rate/", {"resource_id": self.resource.id, "rating": 4})
        self.assertEqual(resp.status_code, 201)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.avg_rating, 4.0)
        self.assertEqual(self.resource.rating_count, 1)

    def test_update_rate(self):
        self.client.post("/api/behaviors/rate/", {"resource_id": self.resource.id, "rating": 3})
        resp = self.client.post("/api/behaviors/rate/", {"resource_id": self.resource.id, "rating": 5})
        self.assertEqual(resp.status_code, 200)
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.avg_rating, 5.0)
        self.assertEqual(self.resource.rating_count, 1)

    def test_rate_list(self):
        UserBehavior.objects.create(user=self.user, resource=self.resource, behavior_type="rate", rating=4)
        resp = self.client.get("/api/behaviors/ratings/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["results"]), 1)
