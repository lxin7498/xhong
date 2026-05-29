"""
生成仿真评分数据，让 CF 评估有意义

原理：
- 将用户分为 3 个"品味群组"，每组偏好不同的资源类别
- 同组用户评分高度重叠（~70%），模拟真实兴趣社群
- 留 2 个冷启动用户（< 5 条评分）
- 评分带噪声，模拟真实场景

用法: python manage.py generate_ratings [--clear] [--min-per-user 15] [--max-per-user 25]
"""

import random
import numpy as np
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count

from apps.behaviors.models import UserBehavior
from apps.resources.models import Resource

User = get_user_model()

# 3 个品味群组 → 不同类别偏好
CLUSTER_PREFERENCES = [
    {  # 群组 0: 偏前端/编程/文章
        "categories": ["前端", "编程", "JavaScript", "Python", "CSS"],
        "difficulty_weight": {"beginner": 0.5, "intermediate": 0.3, "advanced": 0.2},
    },
    {  # 群组 1: 偏系统/网络/AI
        "categories": ["系统", "网络", "AI", "机器学习", "后端", "数据库"],
        "difficulty_weight": {"beginner": 0.2, "intermediate": 0.4, "advanced": 0.4},
    },
    {  # 群组 2: 综合/混合
        "categories": None,  # 不限制类别
        "difficulty_weight": {"beginner": 0.35, "intermediate": 0.35, "advanced": 0.3},
    },
]

MIN_PER_USER = 15
MAX_PER_USER = 25
COLD_START_COUNT = 2  # 保留冷启动用户数量
OVERLAP_RATIO = 0.65  # 同组用户共享资源比例


def score_resource_for_cluster(resource, cluster_idx):
    """
    根据群组偏好给资源打分（用于加权采样）。
    返回 0~1 的概率权重。
    """
    pref = CLUSTER_PREFERENCES[cluster_idx]
    score = 0.3  # 基础分

    # 类别匹配
    cats = pref.get("categories")
    if cats is None:
        score += 0.4  # 综合群组，所有类别平等
    elif resource.category in cats:
        score += 0.5
    elif any(c in (resource.category or "") for c in cats):
        score += 0.25

    # 难度权重
    diff_w = pref["difficulty_weight"].get(resource.difficulty, 0.25)
    score += diff_w * 0.3

    return min(score, 1.0)


class Command(BaseCommand):
    help = "生成仿真评分数据，创建有意义的 CF 评估基线"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true", help="先清除所有评分记录")
        parser.add_argument("--min-per-user", type=int, default=MIN_PER_USER)
        parser.add_argument("--max-per-user", type=int, default=MAX_PER_USER)
        parser.add_argument("--seed", type=int, default=42, help="随机种子")

    def handle(self, *args, **options):
        random.seed(options["seed"])
        np.random.seed(options["seed"])

        if options["clear"]:
            deleted, _ = UserBehavior.objects.filter(behavior_type="rate").delete()
            self.stdout.write(f"  已清除 {deleted} 条评分记录")
            # 重置资源的评分统计
            Resource.objects.update(avg_rating=0, rating_count=0)

        resources = list(Resource.objects.all())
        if not resources:
            self.stdout.write(self.style.ERROR("  没有资源，请先导入资源数据"))
            return

        self.stdout.write(f"  资源总数: {len(resources)}")

        # 按类别分组
        by_category = defaultdict(list)
        for r in resources:
            by_category[r.category].append(r)
        self.stdout.write(f"  资源类别: {len(by_category)} 个")
        for cat, items in sorted(by_category.items()):
            self.stdout.write(f"    {cat}: {len(items)} 个")

        # 获取非 staff 用户（排除 admin）
        users = list(User.objects.filter(is_staff=False).order_by("id"))
        if not users:
            self.stdout.write(self.style.ERROR("  没有普通用户"))
            return

        self.stdout.write(f"\n  普通用户: {len(users)} 个")

        # 用户分组：轮流分配到 3 个群组
        clusters = defaultdict(list)
        for i, user in enumerate(users):
            cluster = i % 3
            clusters[cluster].append(user)

        # 处理每个群组
        total_generated = 0
        existing_rates = set(
            UserBehavior.objects.filter(behavior_type="rate").values_list("user_id", "resource_id")
        )

        for cluster_idx in range(3):
            cluster_users = clusters[cluster_idx]
            if not cluster_users:
                continue

            pref = CLUSTER_PREFERENCES[cluster_idx]

            # 为该群组筛选"核心资源池"（加权排序）
            scored = [(score_resource_for_cluster(r, cluster_idx), r) for r in resources]
            scored.sort(key=lambda x: x[0], reverse=True)

            # 群组核心资源池（取前 ~70% 加权高的资源）
            pool_size = max(int(len(resources) * 0.7), 20)
            core_pool = [r for _, r in scored[:pool_size]]

            self.stdout.write(f"\n  群组 {cluster_idx} ({len(cluster_users)} 用户)")
            cats_str = pref.get("categories")
            if cats_str:
                self.stdout.write(f"    偏好类别: {', '.join(cats_str[:5])}")
            self.stdout.write(f"    核心资源池: {len(core_pool)} 个")

            # 生成该群组的"共享评分集"（用户之间重叠的来源）
            shared_pool_size = int(len(core_pool) * OVERLAP_RATIO)
            shared_resources = random.sample(core_pool, shared_pool_size)

            # 为群组中的每个用户生成评分
            for i, user in enumerate(cluster_users):
                # 最后 COLD_START_COUNT 个用户保持冷启动状态
                if i >= len(cluster_users) - COLD_START_COUNT:
                    n_ratings = random.randint(2, 4)
                    is_cold = True
                else:
                    n_ratings = random.randint(
                        max(options["min_per_user"], shared_pool_size // 2),
                        options["max_per_user"],
                    )
                    is_cold = False

                # 共享部分（~65% 来自共享池） + 个人部分（~35% 随机）
                n_shared = int(n_ratings * 0.65)
                n_personal = n_ratings - n_shared

                user_rated = set()
                user_behaviors = []

                # 共享资源（同组用户间产生重叠）
                available_shared = [
                    r for r in shared_resources
                    if (user.id, r.id) not in existing_rates
                ]
                n_shared = min(n_shared, len(available_shared))
                for r in random.sample(available_shared, n_shared):
                    user_rated.add(r.id)
                    rating = self._generate_rating(r, cluster_idx, is_shared=True)
                    user_behaviors.append(
                        UserBehavior(
                            user=user,
                            resource=r,
                            behavior_type="rate",
                            rating=rating,
                        )
                    )

                # 个人资源（从核心池中选未评分的）
                available_personal = [
                    r for r in core_pool
                    if r.id not in user_rated
                    and (user.id, r.id) not in existing_rates
                ]
                n_personal = min(n_personal, len(available_personal))
                for r in random.sample(available_personal, n_personal):
                    rating = self._generate_rating(r, cluster_idx, is_shared=False)
                    user_behaviors.append(
                        UserBehavior(
                            user=user,
                            resource=r,
                            behavior_type="rate",
                            rating=rating,
                        )
                    )

                if user_behaviors:
                    UserBehavior.objects.bulk_create(user_behaviors)
                    total_generated += len(user_behaviors)

                tag = "❄️ 冷启动" if is_cold else ""
                self.stdout.write(
                    f"    用户 {user.id} ({user.username}): {len(user_behaviors)} 条评分 {tag}"
                )

        self.stdout.write(f"\n  ✅ 共生成 {total_generated} 条评分")

        # 更新资源评分统计
        self._update_resource_stats()
        self.stdout.write("  ✅ 资源评分统计已更新")

    def _generate_rating(self, resource, cluster_idx, is_shared):
        """
        生成带噪声的评分 (1-5)。
        - 同组共享资源偏高（4-5）
        - 个人资源略低（3-4）
        - 加一点随机噪声
        """
        if is_shared:
            base = 4.5  # 共享资源说明该群组用户普遍喜欢
        else:
            base = 3.5

        noise = np.random.normal(0, 0.4)
        rating = round(base + noise)
        return max(1, min(5, rating))

    @staticmethod
    def _update_resource_stats():
        """重新计算每个资源的 avg_rating 和 rating_count"""
        stats = (
            UserBehavior.objects.filter(behavior_type="rate")
            .values("resource_id")
            .annotate(count=Count("id"), avg=Count("rating"))
        )
        # 用原始 SQL 更新更高效
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE resources_resource
                SET
                    rating_count = (
                        SELECT COUNT(*) FROM behaviors_userbehavior
                        WHERE behaviors_userbehavior.resource_id = resources_resource.id
                        AND behaviors_userbehavior.behavior_type = 'rate'
                    ),
                    avg_rating = COALESCE((
                        SELECT AVG(rating) FROM behaviors_userbehavior
                        WHERE behaviors_userbehavior.resource_id = resources_resource.id
                        AND behaviors_userbehavior.behavior_type = 'rate'
                    ), 0)
            """)
