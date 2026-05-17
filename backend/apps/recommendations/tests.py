from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.resources.models import Resource
from apps.behaviors.models import UserBehavior
from apps.recommendations.engine import (
    _build_rating_matrix,
    _compute_similarity,
    compute_recommendations,
    get_recommendations,
)

User = get_user_model()


def _add_dummy_rating(resource, user=None):
    """Add a rating to a resource so cold-start picks it up."""
    if user is None:
        user = User.objects.create_user(username=f"cold_user_{resource.id}", password="pass")
    UserBehavior.objects.create(user=user, resource=resource, behavior_type="rate", rating=4)
    resource.refresh_from_db()


class ColdStartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="newbie", password="pass")
        for i in range(3):
            r = Resource.objects.create(
                title=f"Resource {i}",
                resource_type="video", category="CS",
                url=f"http://example.com/{i}",
                avg_rating=4.0 + i * 0.2,
                browse_count=100 - i * 10,
            )
            # Cold start needs rated resources
            _add_dummy_rating(r)

    def test_cold_start_below_threshold(self):
        UserBehavior.objects.create(
            user=self.user, resource=Resource.objects.first(), behavior_type="browse",
        )
        result = compute_recommendations(self.user)
        self.assertTrue(result["cold_start"])
        self.assertTrue(len(result["items"]) > 0)

    def test_cold_start_no_behaviors(self):
        result = compute_recommendations(self.user)
        self.assertTrue(result["cold_start"])
        self.assertTrue(len(result["items"]) > 0)


class RatingMatrixTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(username="u1", password="pass")
        self.u2 = User.objects.create_user(username="u2", password="pass")
        self.r1 = Resource.objects.create(title="R1", resource_type="video", category="A", url="http://a.com")
        self.r2 = Resource.objects.create(title="R2", resource_type="video", category="A", url="http://b.com")

    def test_build_matrix_returns_none_when_no_ratings(self):
        matrix, user_ids, resource_ids, _, _ = _build_rating_matrix()
        self.assertIsNone(matrix)

    def test_build_matrix_shape(self):
        UserBehavior.objects.create(user=self.u1, resource=self.r1, behavior_type="rate", rating=4)
        UserBehavior.objects.create(user=self.u1, resource=self.r2, behavior_type="rate", rating=3)
        UserBehavior.objects.create(user=self.u2, resource=self.r1, behavior_type="rate", rating=5)
        matrix, _, _, _, _ = _build_rating_matrix()
        self.assertIsNotNone(matrix)
        self.assertEqual(matrix.shape, (2, 2))

    def test_similarity_computation(self):
        UserBehavior.objects.create(user=self.u1, resource=self.r1, behavior_type="rate", rating=5)
        UserBehavior.objects.create(user=self.u1, resource=self.r2, behavior_type="rate", rating=1)
        UserBehavior.objects.create(user=self.u2, resource=self.r1, behavior_type="rate", rating=5)
        UserBehavior.objects.create(user=self.u2, resource=self.r2, behavior_type="rate", rating=1)
        matrix, _, _, _, _ = _build_rating_matrix()
        similarity, _ = _compute_similarity(matrix)
        self.assertEqual(similarity.shape, (2, 2))
        self.assertGreater(similarity[0, 1], 0.9)


class CFRecommendationTests(TestCase):
    def setUp(self):
        self.target = User.objects.create_user(username="target", password="pass")
        self.others = [
            User.objects.create_user(username=f"o{i}", password="pass") for i in range(3)
        ]
        self.resources = []
        for i in range(8):
            self.resources.append(Resource.objects.create(
                title=f"R{i}", resource_type="video", category="CS",
                url=f"http://example.com/r{i}",
            ))

    def _add_ratings(self):
        for j, other in enumerate(self.others):
            for i, r in enumerate(self.resources[:6]):
                UserBehavior.objects.create(
                    user=other, resource=r, behavior_type="rate", rating=3 + (i + j) % 3
                )
        # Target rates 5 resources to exceed cold start threshold
        for i, r in enumerate(self.resources[:5]):
            UserBehavior.objects.create(
                user=self.target, resource=r, behavior_type="rate", rating=4 + i % 2
            )

    def test_cf_recommends_unrated_resources(self):
        self._add_ratings()
        result = compute_recommendations(self.target)
        self.assertFalse(result["cold_start"])
        recommended_ids = result["items"]
        rated_ids = [r.id for r in self.resources[:5]]
        for rid in recommended_ids:
            self.assertNotIn(rid, rated_ids)

    def test_cache_returns_same_result(self):
        self._add_ratings()
        r1 = get_recommendations(self.target)
        r2 = get_recommendations(self.target)
        self.assertEqual(r1["items"], r2["items"])

    def test_falls_back_to_cold_start_with_only_browses(self):
        for i in range(5):
            UserBehavior.objects.create(
                user=self.target, resource=self.resources[i], behavior_type="browse"
            )
        result = compute_recommendations(self.target)
        self.assertTrue(result["cold_start"])
