"""
推荐系统离线评估模块

指标：
- Precision@K, Recall@K, NDCG@K
- Coverage (推荐覆盖率)
- Cold-start Hit Rate (冷启动命中率)

对比：
- Popularity 热门推荐（基线）
- User-Based CF 协同过滤
"""

import numpy as np
from collections import defaultdict
from dataclasses import dataclass, field

from django.contrib.auth import get_user_model
from apps.behaviors.models import UserBehavior
from apps.resources.models import Resource

User = get_user_model()

COLD_START_THRESHOLD = 5
NEIGHBOR_K = 20
DEFAULT_K_VALUES = (5, 9)
RELEVANCE_THRESHOLD = 4  # 评分 >= 4 视为相关


# ---------------------------------------------------------------------------
# 数据切分
# ---------------------------------------------------------------------------

def split_train_test(ratio=0.8):
    """
    按时间顺序对每个用户的评分做 train/test 切分。
    返回: (train_behaviors, test_behaviors) — 两个 UserBehavior 列表
    """
    all_rates = list(
        UserBehavior.objects.filter(behavior_type=UserBehavior.BehaviorType.RATE)
        .select_related("user", "resource")
        .order_by("created_at")
    )

    user_buckets = defaultdict(list)
    for b in all_rates:
        user_buckets[b.user_id].append(b)

    train, test = [], []
    for uid, behaviors in user_buckets.items():
        n = len(behaviors)
        split_idx = int(n * ratio)
        # 保证 train 和 test 都至少有 1 条，否则全部放 train
        if split_idx == 0 and n >= 2:
            split_idx = 1
        elif split_idx == n and n >= 2:
            split_idx = n - 1

        train.extend(behaviors[:split_idx])
        test.extend(behaviors[split_idx:])

    return train, test


# ---------------------------------------------------------------------------
# 辅助：从 behavior 列表构建评分矩阵
# ---------------------------------------------------------------------------

def _build_matrix_from_behaviors(behaviors):
    """从给定的 behavior 列表构建评分矩阵，返回和 engine._build_rating_matrix 相同的结构"""
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
    """Cosine similarity on mean-centered ratings"""
    user_means = np.nanmean(matrix, axis=1, keepdims=True)
    centered = np.nan_to_num(matrix - user_means, 0)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    norms[norms == 0] = 1
    normalized = centered / norms
    similarity = normalized @ normalized.T
    return similarity, user_means


# ---------------------------------------------------------------------------
# 热门推荐基线
# ---------------------------------------------------------------------------

class PopularityRecommender:
    """
    基于训练集的热门推荐：按 (评分次数 × 平均评分) 综合排序。
    排除用户已评分的资源。
    """

    def __init__(self, train_behaviors):
        # 统计每个资源的评分信息
        res_ratings = defaultdict(list)
        for b in train_behaviors:
            res_ratings[b.resource_id].append(b.rating)

        self.resource_stats = {}
        for rid, ratings in res_ratings.items():
            arr = np.array(ratings, dtype=float)
            self.resource_stats[rid] = {
                "count": len(arr),
                "avg": float(np.mean(arr)),
                "score": len(arr) * float(np.mean(arr)),  # 综合分
            }

        # 按综合分排序的资源列表
        self.ranked = sorted(
            self.resource_stats.keys(),
            key=lambda rid: self.resource_stats[rid]["score"],
            reverse=True,
        )

        # 每个用户已评分的资源集合
        self.user_rated = defaultdict(set)
        for b in train_behaviors:
            self.user_rated[b.user_id].add(b.resource_id)

    def recommend(self, user_id, top_n=9):
        rated = self.user_rated.get(user_id, set())
        recs = []
        for rid in self.ranked:
            if rid not in rated:
                recs.append(rid)
            if len(recs) >= top_n:
                break
        return recs


# ---------------------------------------------------------------------------
# 协同过滤推荐器（离线评估用）
# ---------------------------------------------------------------------------

class CFRecommender:
    """用训练集数据构建评分矩阵，做 UBCF 预测"""

    def __init__(self, train_behaviors):
        self.matrix, self.user_ids, self.resource_ids, self.user_idx, self.resource_idx = (
            _build_matrix_from_behaviors(train_behaviors)
        )
        self.similarity = None
        self.user_means = None
        if self.matrix is not None and self.matrix.shape[0] >= 2:
            self.similarity, self.user_means = _compute_similarity(self.matrix)

    def recommend(self, user_id, top_n=9):
        if self.matrix is None or user_id not in self.user_idx:
            return []

        if self.matrix.shape[0] < 2 or self.similarity is None:
            return []

        target_idx = self.user_idx[user_id]
        target_sim = self.similarity[target_idx]

        neighbor_indices = np.argsort(target_sim)[::-1]
        neighbor_indices = neighbor_indices[neighbor_indices != target_idx][:NEIGHBOR_K]

        predictions = []
        for j in range(self.matrix.shape[1]):
            if not np.isnan(self.matrix[target_idx, j]):
                continue  # 跳过已评分

            neighbor_ratings = self.matrix[neighbor_indices, j]
            valid = ~np.isnan(neighbor_ratings)
            valid_idx = neighbor_indices[valid]
            valid_ratings = neighbor_ratings[valid]

            if len(valid_idx) < 2:
                continue

            sims = target_sim[valid_idx]
            abs_sum = np.sum(np.abs(sims))
            if abs_sum == 0:
                continue

            target_mean = self.user_means[target_idx, 0]
            neighbor_means = self.user_means[valid_idx, 0]
            pred = target_mean + np.sum(sims * (valid_ratings - neighbor_means)) / abs_sum
            pred = max(1.0, min(5.0, pred))
            predictions.append((self.resource_ids[j], round(pred, 2)))

        predictions.sort(key=lambda x: x[1], reverse=True)
        return [rid for rid, _ in predictions[:top_n]]

    def predict_rating(self, user_id, resource_id):
        """预测单个用户对单个资源的评分，返回 (predicted_rating, actual_rating) 或 None"""
        if self.matrix is None or user_id not in self.user_idx:
            return None
        if resource_id not in self.resource_idx:
            return None
        if self.matrix.shape[0] < 2 or self.similarity is None:
            return None

        target_idx = self.user_idx[user_id]
        target_sim = self.similarity[target_idx]
        j = self.resource_idx[resource_id]

        # Return actual rating if already rated (for evaluation we compare against test set)
        neighbor_indices = np.argsort(target_sim)[::-1]
        neighbor_indices = neighbor_indices[neighbor_indices != target_idx][:NEIGHBOR_K]

        neighbor_ratings = self.matrix[neighbor_indices, j]
        valid = ~np.isnan(neighbor_ratings)
        valid_idx = neighbor_indices[valid]
        valid_ratings = neighbor_ratings[valid]

        if len(valid_idx) < 2:
            return None

        sims = target_sim[valid_idx]
        abs_sum = np.sum(np.abs(sims))
        if abs_sum == 0:
            return None

        target_mean = self.user_means[target_idx, 0]
        neighbor_means = self.user_means[valid_idx, 0]
        pred = target_mean + np.sum(sims * (valid_ratings - neighbor_means)) / abs_sum
        pred = max(1.0, min(5.0, pred))
        return round(pred, 2)


# ---------------------------------------------------------------------------
# 评估指标
# ---------------------------------------------------------------------------

def precision_at_k(recommended, relevant, k):
    """Precision@K = |推荐 ∩ 相关| / K"""
    if k <= 0:
        return 0.0
    rec_k = set(recommended[:k])
    rel = set(relevant)
    return len(rec_k & rel) / k


def recall_at_k(recommended, relevant, k):
    """Recall@K = |推荐 ∩ 相关| / |相关|"""
    rec_k = set(recommended[:k])
    rel = set(relevant)
    if len(rel) == 0:
        return 0.0
    return len(rec_k & rel) / len(rel)


def dcg_at_k(ranked_relevances, k):
    """DCG@K"""
    dcg = 0.0
    for i, rel in enumerate(ranked_relevances[:k]):
        dcg += rel / np.log2(i + 2)  # i 从 0 开始，log2(i+2)
    return dcg


def ndcg_at_k(recommended, ratings_dict, k):
    """
    NDCG@K: 用实际评分作为相关性分数 (1-5 分)
    ratings_dict: {resource_id: actual_rating_in_test_set}
    """
    if k <= 0:
        return 0.0

    # 推荐列表对应的相关性分数
    rec_relevances = [ratings_dict.get(rid, 0) for rid in recommended[:k]]
    dcg = dcg_at_k(rec_relevances, k)

    # 理想排序：取测试集中所有评分，降序排列
    ideal = sorted(ratings_dict.values(), reverse=True)
    idcg = dcg_at_k(ideal, k)

    if idcg == 0:
        return 0.0
    return dcg / idcg


def coverage(all_recommendations, total_items):
    """覆盖率 = 推荐过的不同资源数 / 总资源数"""
    if total_items == 0:
        return 0.0
    unique = set()
    for recs in all_recommendations.values():
        unique.update(recs)
    return len(unique) / total_items


def rmse(predictions, actuals):
    """RMSE = sqrt(mean((pred - actual)²))"""
    if len(predictions) == 0:
        return 0.0
    squared_errors = [(p - a) ** 2 for p, a in zip(predictions, actuals)]
    return round(float(np.sqrt(np.mean(squared_errors))), 4)


# ---------------------------------------------------------------------------
# 评估执行
# ---------------------------------------------------------------------------

@dataclass
class MetricResult:
    precision_5: float = 0.0
    recall_5: float = 0.0
    ndcg_5: float = 0.0
    precision_9: float = 0.0
    recall_9: float = 0.0
    ndcg_9: float = 0.0
    coverage: float = 0.0
    rmse: float = 0.0
    cold_start_hit_rate: float = 0.0
    cold_start_count: int = 0
    cold_start_hit_count: int = 0
    total_users: int = 0
    evaluable_users: int = 0  # 有测试评分的用户数


def run_evaluation():
    """
    执行完整评估流程，返回 (popularity_result, cf_result) 两个 MetricResult。
    结果也会缓存到 Django cache (key: recs:eval:result)，供 API 读取。
    """
    from django.core.cache import cache

    train, test = split_train_test(ratio=0.8)

    # ---------- 按用户组织测试集 ----------
    test_user_ratings = defaultdict(dict)  # {user_id: {resource_id: rating}}
    test_user_relevants = defaultdict(set)  # {user_id: {resource_id where rating >= 4}}
    for b in test:
        test_user_ratings[b.user_id][b.resource_id] = b.rating
        if b.rating >= RELEVANCE_THRESHOLD:
            test_user_relevants[b.user_id].add(b.resource_id)

    evaluable_users = [uid for uid in test_user_ratings if len(test_user_ratings[uid]) > 0]

    # 总资源数（训练集中的所有资源 + 测试集中的资源）
    all_resource_ids = set()
    for b in train:
        all_resource_ids.add(b.resource_id)
    for b in test:
        all_resource_ids.add(b.resource_id)
    total_items = len(all_resource_ids)

    # 训练集中每个用户的行为数（用于判断冷启动）
    train_user_behavior_count = defaultdict(int)
    for b in train:
        train_user_behavior_count[b.user_id] += 1

    # ---------- 初始化推荐器 ----------
    pop = PopularityRecommender(train)
    cf = CFRecommender(train)

    # ---------- 评估函数 ----------
    def evaluate_one(recommender, label, is_cf=False):
        prec_5_vals, recall_5_vals, ndcg_5_vals = [], [], []
        prec_9_vals, recall_9_vals, ndcg_9_vals = [], [], []
        all_recs = {}
        pred_ratings = []
        actual_ratings = []

        cold_count = 0
        cold_hit = 0

        for uid in evaluable_users:
            recs = recommender.recommend(uid, top_n=9)
            all_recs[uid] = recs
            ratings = test_user_ratings[uid]
            relevants = test_user_relevants[uid]

            # RMSE: 对测试集中每个实际评分，用 CF 预测评分
            if is_cf and hasattr(recommender, 'predict_rating'):
                for rid, actual in ratings.items():
                    pred = recommender.predict_rating(uid, rid)
                    if pred is not None:
                        pred_ratings.append(pred)
                        actual_ratings.append(actual)

            # Precision & Recall
            p5 = precision_at_k(recs, relevants, 5)
            r5 = recall_at_k(recs, relevants, 5)
            p9 = precision_at_k(recs, relevants, 9)
            r9 = recall_at_k(recs, relevants, 9)

            prec_5_vals.append(p5)
            recall_5_vals.append(r5)
            prec_9_vals.append(p9)
            recall_9_vals.append(r9)

            # NDCG
            n5 = ndcg_at_k(recs, ratings, 5)
            n9 = ndcg_at_k(recs, ratings, 9)
            ndcg_5_vals.append(n5)
            ndcg_9_vals.append(n9)

            # Cold-start hit rate
            is_cold = train_user_behavior_count.get(uid, 0) < COLD_START_THRESHOLD
            if is_cold:
                cold_count += 1
                if len(set(recs) & set(relevants)) > 0:
                    cold_hit += 1

        n_users = len(evaluable_users) or 1
        cov = coverage(all_recs, total_items)
        cs_hr = cold_hit / cold_count if cold_count > 0 else 0.0
        rmse_val = rmse(pred_ratings, actual_ratings) if is_cf else 0.0

        result = MetricResult(
            precision_5=round(np.mean(prec_5_vals), 4) if prec_5_vals else 0.0,
            recall_5=round(np.mean(recall_5_vals), 4) if recall_5_vals else 0.0,
            ndcg_5=round(np.mean(ndcg_5_vals), 4) if ndcg_5_vals else 0.0,
            precision_9=round(np.mean(prec_9_vals), 4) if prec_9_vals else 0.0,
            recall_9=round(np.mean(recall_9_vals), 4) if recall_9_vals else 0.0,
            ndcg_9=round(np.mean(ndcg_9_vals), 4) if ndcg_9_vals else 0.0,
            coverage=round(cov, 4),
            rmse=rmse_val,
            cold_start_hit_rate=round(cs_hr, 4),
            cold_start_count=cold_count,
            cold_start_hit_count=cold_hit,
            total_users=len(evaluable_users),
            evaluable_users=n_users,
        )
        return result

    pop_result = evaluate_one(pop, "Popularity", is_cf=False)
    cf_result = evaluate_one(cf, "CF", is_cf=True)

    # 缓存结果 1 小时
    cache.set("recs:eval:result", {
        "popularity": pop_result,
        "cf": cf_result,
    }, 3600)

    return pop_result, cf_result


def get_cached_evaluation():
    """读取缓存的评估结果，无缓存时重新计算"""
    from django.core.cache import cache

    cached = cache.get("recs:eval:result")
    if cached:
        return cached["popularity"], cached["cf"]

    return run_evaluation()
