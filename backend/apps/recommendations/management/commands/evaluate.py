"""
推荐系统离线评估命令

用法: python manage.py evaluate
"""

from django.core.management.base import BaseCommand

from apps.recommendations.evaluation import run_evaluation, COLD_START_THRESHOLD


def fmt_pct(val):
    """格式化为百分比字符串"""
    return f"{val * 100:.2f}%"


def fmt_metric(a, b, higher_better=True):
    """
    格式化指标对比：标注优胜方。
    higher_better=True  → 值越大越好 (Precision/Recall/NDCG/Coverage/CSHR)
    """
    a_str = f"{a:.4f}"
    b_str = f"{b:.4f}"
    if a == b:
        return a_str, b_str, "—"
    a_win = (a > b) if higher_better else (a < b)
    if a_win:
        return f"★ {a_str}", b_str, "Popularity"
    else:
        return a_str, f"★ {b_str}", "CF"


class Command(BaseCommand):
    help = "评估推荐系统指标：Popularity vs Collaborative Filtering"

    def handle(self, *args, **options):
        self.stdout.write("=" * 72)
        self.stdout.write("  推荐系统离线评估")
        self.stdout.write("=" * 72)
        self.stdout.write("")
        self.stdout.write("  冷启动阈值: {} 条行为".format(COLD_START_THRESHOLD))
        self.stdout.write("  相关性阈值: 评分 ≥ 4")
        self.stdout.write("  数据切分: 时间顺序 80/20")
        self.stdout.write("")

        # 运行评估
        pop, cf = run_evaluation()

        self.stdout.write(f"  可评估用户数: {pop.evaluable_users}")
        self.stdout.write(f"  其中冷启动用户: {pop.cold_start_count}")
        self.stdout.write("")

        # ---------- 指标对比表 ----------
        header = f"  {'指标':<26} {'Popularity':>12} {'CF':>12} {'优胜':>10}"
        sep = "  " + "-" * 62
        self.stdout.write(header)
        self.stdout.write(sep)

        rows = [
            ("Precision@5",  pop.precision_5,  cf.precision_5,  True),
            ("Recall@5",     pop.recall_5,     cf.recall_5,     True),
            ("NDCG@5",       pop.ndcg_5,       cf.ndcg_5,       True),
            ("Precision@9",  pop.precision_9,  cf.precision_9,  True),
            ("Recall@9",     pop.recall_9,     cf.recall_9,     True),
            ("NDCG@9",       pop.ndcg_9,       cf.ndcg_9,       True),
            ("Coverage",     pop.coverage,     cf.coverage,     True),
            ("RMSE (仅CF)",  0.0,              cf.rmse,         False),  # RMSE 越小越好，仅 CF 有
            ("冷启动命中率", pop.cold_start_hit_rate, cf.cold_start_hit_rate, True),
        ]

        for label, pv, cv, higher in rows:
            if "RMSE" in label:
                # Popularity 无 RMSE，只展示 CF 的值
                self.stdout.write(f"  {label:<26} {'N/A':>12} {cv:>12.4f} {'—':>10}")
            else:
                p_str, c_str, winner = fmt_metric(pv, cv, higher)
                self.stdout.write(f"  {label:<26} {p_str:>12} {c_str:>12} {winner:>10}")

        self.stdout.write(sep)
        self.stdout.write("")

        # 冷启动详情
        self.stdout.write(f"  冷启动命中详情 (Popularity): {pop.cold_start_hit_count}/{pop.cold_start_count}")
        self.stdout.write(f"  冷启动命中详情 (CF):         {cf.cold_start_hit_count}/{cf.cold_start_count}")
        self.stdout.write("")

        # 结论
        pop_wins = 0
        cf_wins = 0
        for _, pv, cv, higher in rows:
            if pv == cv:
                continue
            if isinstance(pv, float) and pv == 0.0 and cv > 0 and not higher:
                continue  # Skip RMSE: Popularity has no RMSE
            if higher:
                if pv > cv:
                    pop_wins += 1
                else:
                    cf_wins += 1
            else:
                if pv < cv:
                    pop_wins += 1
                else:
                    cf_wins += 1

        self.stdout.write(f"  综合: Popularity 胜 {pop_wins} 项, CF 胜 {cf_wins} 项")
        self.stdout.write("")
        self.stdout.write("=" * 72)
