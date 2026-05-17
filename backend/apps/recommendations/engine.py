import numpy as np
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import Log

from apps.behaviors.models import UserBehavior
from apps.resources.models import Resource

User = get_user_model()

COLD_START_THRESHOLD = 5
NEIGHBOR_K = 20
TOP_N = 20
CACHE_TTL = 3600


def _build_rating_matrix():
    behaviors = UserBehavior.objects.filter(
        behavior_type=UserBehavior.BehaviorType.RATE,
    ).select_related("user", "resource")

    user_ids = sorted(set(b.user_id for b in behaviors))
    resource_ids = sorted(set(b.resource_id for b in behaviors))

    if not user_ids or not resource_ids:
        return None, [], [], {}, {}

    user_idx = {uid: i for i, uid in enumerate(user_ids)}
    resource_idx = {rid: i for i, rid in enumerate(resource_ids)}

    matrix = np.full((len(user_ids), len(resource_ids)), np.nan)
    for b in behaviors:
        ui = user_idx[b.user_id]
        ri = resource_idx[b.resource_id]
        matrix[ui, ri] = b.rating

    return matrix, user_ids, resource_ids, user_idx, resource_idx


def _compute_similarity(matrix):
    user_means = np.nanmean(matrix, axis=1, keepdims=True)
    centered = np.nan_to_num(matrix - user_means, 0)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = centered / norms
    similarity = normalized @ normalized.T
    return similarity, user_means


def _predict_for_user(target_uid, matrix, user_ids, resource_ids, similarity, user_means):
    target_idx = user_ids.index(target_uid)
    target_sim = similarity[target_idx]

    neighbor_indices = np.argsort(target_sim)[::-1]
    neighbor_indices = neighbor_indices[neighbor_indices != target_idx][:NEIGHBOR_K]

    predictions = []
    for j in range(matrix.shape[1]):
        if not np.isnan(matrix[target_idx, j]):
            continue

        neighbor_ratings = matrix[neighbor_indices, j]
        valid = ~np.isnan(neighbor_ratings)
        valid_idx = neighbor_indices[valid]
        valid_ratings = neighbor_ratings[valid]

        if len(valid_idx) < 2:
            continue

        sims = target_sim[valid_idx]
        abs_sum = np.sum(np.abs(sims))
        if abs_sum == 0:
            continue

        target_mean = user_means[target_idx, 0]
        neighbor_means = user_means[valid_idx, 0]
        pred = target_mean + np.sum(sims * (valid_ratings - neighbor_means)) / abs_sum
        pred = max(1.0, min(5.0, pred))
        predictions.append((resource_ids[j], round(pred, 2)))

    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions[:TOP_N]


def _cold_start_recommendations():
    """Popular resources: prefer those with real ratings, then fall back to cached rating_count."""
    rated = list(
        Resource.objects.annotate(
            rate_count=Count("behaviors", filter=Q(behaviors__behavior_type="rate")),
        )
        .filter(rate_count__gte=1)
        .order_by("-avg_rating", "-browse_count")
        .values_list("id", flat=True)
    )
    if len(rated) >= TOP_N:
        return rated[:TOP_N]

    # Fill with resources that have cached ratings
    fill = list(
        Resource.objects.filter(rating_count__gte=1)
        .exclude(id__in=rated)
        .order_by("-avg_rating", "-browse_count")
        .values_list("id", flat=True)[: TOP_N - len(rated)]
    )
    return rated + fill


def compute_recommendations(user):
    behavior_count = UserBehavior.objects.filter(user=user).count()

    if behavior_count < COLD_START_THRESHOLD:
        ids = _cold_start_recommendations()
        return {"items": ids, "cold_start": True, "neighbors": []}

    matrix, user_ids, resource_ids, user_idx, resource_idx = _build_rating_matrix()

    if matrix is None or user.id not in user_ids:
        ids = _cold_start_recommendations()
        return {"items": ids, "cold_start": True, "neighbors": []}

    similarity, user_means = _compute_similarity(matrix)
    predictions = _predict_for_user(user.id, matrix, user_ids, resource_ids, similarity, user_means)

    if not predictions:
        ids = _cold_start_recommendations()
        return {"items": ids, "cold_start": True, "neighbors": []}

    return {
        "items": [rid for rid, _ in predictions],
        "cold_start": False,
    }


def get_recommendations(user, refresh=False):
    cache_key = f"recs:{user.id}"
    if not refresh:
        cached = cache.get(cache_key)
        if cached:
            return cached

    result = compute_recommendations(user)
    cache.set(cache_key, result, CACHE_TTL)
    return result


def refresh_recommendations(user):
    cache.delete(f"recs:{user.id}")
    return get_recommendations(user, refresh=True)
