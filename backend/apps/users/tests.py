from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="test", password="pass123")
        self.assertEqual(user.username, "test")
        self.assertTrue(user.check_password("pass123"))

    def test_user_profile_auto_created_by_signal(self):
        user = User.objects.create_user(username="test", password="pass")
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.nickname, "")

    def test_user_profile_update(self):
        user = User.objects.create_user(username="test", password="pass")
        user.profile.major = "软件工程"
        user.profile.grade = "大三"
        user.profile.interest_tags = ["Python", "机器学习"]
        user.profile.save()
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.major, "软件工程")
        self.assertEqual(user.profile.interest_tags, ["Python", "机器学习"])

    def test_user_profile_defaults(self):
        user = User.objects.create_user(username="test", password="pass")
        self.assertEqual(user.profile.nickname, "")
        self.assertEqual(user.profile.avatar, "")
        self.assertEqual(user.profile.interest_tags, [])


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="authuser", password="testpass123",
        )
        # Signal auto-created profile — update it
        self.user.profile.major = "计算机科学"
        self.user.profile.grade = "大三"
        self.user.profile.save()

    def test_login_returns_tokens(self):
        resp = self.client.post("/api/auth/login/", {
            "username": "authuser", "password": "testpass123",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_invalid_credentials(self):
        resp = self.client.post("/api/auth/login/", {
            "username": "authuser", "password": "wrongpass",
        })
        self.assertEqual(resp.status_code, 401)

    def test_register_creates_user(self):
        resp = self.client.post("/api/auth/register/", {
            "username": "newuser",
            "password": "newpass123",
            "password2": "newpass123",
            "major": "软件工程",
            "grade": "大二",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_without_username(self):
        resp = self.client.post("/api/auth/register/", {
            "password": "pass123",
        })
        self.assertEqual(resp.status_code, 400)

    def test_profile_requires_auth(self):
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 401)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get("/api/users/me/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["username"], "authuser")

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.put("/api/users/me/", {
            "major": "人工智能",
            "interest_tags": ["AI", "Deep Learning"],
        }, format="json")
        self.assertEqual(resp.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.major, "人工智能")
        self.assertEqual(self.user.profile.interest_tags, ["AI", "Deep Learning"])
