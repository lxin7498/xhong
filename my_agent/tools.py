import contextvars
import httpx
from langchain_core.tools import tool
from my_agent.env_utils import DJANGO_BASE_URL

current_token: contextvars.ContextVar[str] = contextvars.ContextVar("token", default="")

# Per-request call counters to prevent excessive tool usage
_search_count: contextvars.ContextVar[int] = contextvars.ContextVar("search_count", default=0)
_detail_count: contextvars.ContextVar[int] = contextvars.ContextVar("detail_count", default=0)
_profile_count: contextvars.ContextVar[int] = contextvars.ContextVar("profile_count", default=0)
_behavior_count: contextvars.ContextVar[int] = contextvars.ContextVar("behavior_count", default=0)


def _headers():
    token = current_token.get()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


@tool
async def search_resources(query: str, category: str = "", difficulty: str = "", limit: int = 5) -> str:
    """搜索学习资源。参数：query=搜索关键词，category=分类（可选），difficulty=难度（可选：beginner/intermediate/advanced），limit=返回数量（默认5）"""
    count = _search_count.get() + 1
    _search_count.set(count)
    if count > 1:
        return "重复调用被拒绝：search_resources 已调用过，请直接基于之前的搜索结果回复用户，不要再搜索。"
    params = {"search": query, "page_size": limit}
    if category:
        params["category"] = category
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{DJANGO_BASE_URL}/api/resources/", params=params, headers=_headers())
        if resp.status_code != 200:
            return f"搜索失败: {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return "未找到匹配的资源。"
        items = []
        for r in results:
            items.append(
                f"ID={r['id']} | [{r.get('resource_type','?')}|{r.get('difficulty','?')}] {r['title']} "
                f"— 分类:{r.get('category','?')} | 评分:{r.get('avg_rating',0):.1f} | 浏览:{r.get('browse_count',0)}"
                f"\n  简介: {r.get('description','')[:200]}"
            )
        return "\n".join(items)


@tool
async def get_resource_detail(resource_id: int) -> str:
    """获取某个资源的详细信息，包括链接和标签。参数：resource_id=资源ID"""
    count = _detail_count.get() + 1
    _detail_count.set(count)
    if count > 1:
        return "重复调用被拒绝：get_resource_detail 已调用过，请直接基于已有信息回复。"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{DJANGO_BASE_URL}/api/resources/{resource_id}/", headers=_headers())
        if resp.status_code != 200:
            return f"获取失败: {resp.status_code}"
        r = resp.json()
        return (
            f"ID={r['id']} | [{r.get('resource_type','?')}|{r.get('difficulty','?')}] {r['title']}\n"
            f"分类: {r.get('category','?')}\n"
            f"标签: {', '.join(r.get('tags', []))}\n"
            f"评分: {r.get('avg_rating',0):.1f} ({r.get('rating_count',0)}人评) | 浏览: {r.get('browse_count',0)}\n"
            f"链接: {r.get('url','')}\n"
            f"描述: {r.get('description','')}"
        )


@tool
async def get_user_profile() -> str:
    """获取当前用户的个人信息，包括专业、年级、兴趣标签等。无参数。"""
    count = _profile_count.get() + 1
    _profile_count.set(count)
    if count > 1:
        return "重复调用被拒绝：get_user_profile 已调用过，请直接使用之前的用户画像信息。"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{DJANGO_BASE_URL}/api/users/me/", headers=_headers())
        if resp.status_code != 200:
            return f"获取用户信息失败: {resp.status_code}"
        p = resp.json()
        parts = [
            f"用户名: {p.get('username','?')}",
            f"专业: {p.get('major','未填写')}",
            f"年级: {p.get('grade','未填写')}",
            f"兴趣标签: {', '.join(p.get('interest_tags', [])) if p.get('interest_tags') else '未填写'}",
        ]
        return "\n".join(parts)


@tool
async def get_user_behaviors(behavior_type: str = "all", limit: int = 10) -> str:
    """获取用户近期的行为记录。参数：behavior_type=行为类型（browse/bookmark/rate/all，默认all），limit=返回数量（默认10）"""
    count = _behavior_count.get() + 1
    _behavior_count.set(count)
    if count > 1:
        return "重复调用被拒绝：get_user_behaviors 已调用过，请直接使用之前的行为记录。"
    async with httpx.AsyncClient(timeout=10) as client:
        results = []
        url_map = {"browse": "history", "bookmark": "favorites", "rate": "ratings"}
        types = ["browse", "bookmark", "rate"] if behavior_type == "all" else [behavior_type]
        for bt in types:
            resp = await client.get(
                f"{DJANGO_BASE_URL}/api/behaviors/{url_map[bt]}/",
                params={"page_size": limit},
                headers=_headers(),
            )
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", [])[:limit]:
                    resource = item.get("resource", {})
                    results.append(
                        f"[{bt}] {resource.get('title','?')} — "
                        f"{resource.get('category','?')} | 评分:{resource.get('avg_rating',0):.1f}"
                        + (f" | 我的评分:{item.get('rating')}" if bt == "rate" else "")
                    )
        if not results:
            return "暂无行为记录。"
        return "\n".join(results)
