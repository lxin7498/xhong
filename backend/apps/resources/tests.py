from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Resource

User = get_user_model()


class ResourceModelTests(TestCase):
    def test_create_resource(self):
        r = Resource.objects.create(
            title="Test Python Guide",
            description="A test resource",
            resource_type="article",
            category="Python",
            difficulty="beginner",
            url="https://example.com/test",
        )
        self.assertEqual(r.title, "Test Python Guide")
        self.assertEqual(r.difficulty, "beginner")
        self.assertEqual(r.browse_count, 0)

    def test_str_method(self):
        r = Resource.objects.create(
            title="OS Principles",
            resource_type="video",
            category="OS",
            url="https://example.com/os",
        )
        self.assertEqual(str(r), "OS Principles")

    def test_defaults(self):
        r = Resource.objects.create(title="X", resource_type="article", category="X", url="http://x.com")
        self.assertEqual(r.tags, [])
        self.assertEqual(r.description, "")
        self.assertEqual(r.avg_rating, 0)
        self.assertEqual(r.rating_count, 0)

    def test_meta_ordering(self):
        """Meta.ordering = ['-created_at'] means newest first."""
        self.assertEqual(Resource._meta.ordering, ["-created_at"])


class ResourceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="tester", password="testpass")
        Resource.objects.create(
            title="Python Basics",
            description="Learn Python",
            resource_type="video",
            category="Python",
            tags=["python", "beginner"],
            difficulty="beginner",
            url="https://example.com/py1",
            avg_rating=4.5,
            browse_count=100,
        )
        Resource.objects.create(
            title="Java Advanced",
            description="Deep Java",
            resource_type="article",
            category="Java",
            tags=["java", "advanced"],
            difficulty="advanced",
            url="https://example.com/java1",
            avg_rating=4.0,
            browse_count=50,
        )

    def test_list_all_resources(self):
        resp = self.client.get("/api/resources/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_list_filter_by_category(self):
        resp = self.client.get("/api/resources/?category=Python")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)
        self.assertEqual(resp.data["results"][0]["title"], "Python Basics")

    def test_list_search(self):
        resp = self.client.get("/api/resources/?search=Java")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_list_ordering(self):
        resp = self.client.get("/api/resources/?ordering=browse_count")
        self.assertEqual(resp.status_code, 200)
        titles = [r["title"] for r in resp.data["results"]]
        self.assertEqual(titles[0], "Java Advanced")

    def test_detail_resource(self):
        r = Resource.objects.first()
        resp = self.client.get(f"/api/resources/{r.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["title"], r.title)
        self.assertIn("url", resp.data)

    def test_create_resource_unauthenticated(self):
        resp = self.client.post("/api/resources/", {
            "title": "New", "resource_type": "video", "category": "AI", "url": "http://a.com",
        })
        self.assertEqual(resp.status_code, 401)

    def test_create_resource_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.post("/api/resources/", {
            "title": "New Resource",
            "resource_type": "article",
            "category": "AI",
            "url": "http://example.com/new",
        })
        self.assertEqual(resp.status_code, 403)

    def test_create_resource_admin_succeeds(self):
        admin = User.objects.create_user(username="admin", password="pass", is_staff=True)
        self.client.force_authenticate(user=admin)
        resp = self.client.post("/api/resources/", {
            "title": "New Resource",
            "resource_type": "article",
            "category": "AI",
            "url": "http://example.com/new",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Resource.objects.count(), 3)

    def test_update_resource_admin(self):
        self.client.force_authenticate(user=self.user)
        r = Resource.objects.first()
        resp = self.client.patch(f"/api/resources/{r.id}/", {"title": "Updated"})
        self.assertEqual(resp.status_code, 403)

    def test_delete_resource_unauthenticated(self):
        r = Resource.objects.first()
        resp = self.client.delete(f"/api/resources/{r.id}/")
        self.assertEqual(resp.status_code, 401)
