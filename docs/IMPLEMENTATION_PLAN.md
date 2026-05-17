# 个性化学习资源推荐系统 — 实现计划

## Context
毕设项目：基于协同过滤算法的计算机专业个性化学习资源推荐系统。
技术栈确认：**Django 5 + Vue 3 + MySQL + UserCF**。
新项目零基础搭建，从数据库到前端全栈实现。

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Vue 3 SPA (localhost:5173)                         │
│  Element Plus / Pinia / Vue Router / Axios           │
└────────────┬────────────────────────────────────────┘
             │ REST API (JSON, JWT Bearer Token)
             │ Vite proxy: /api → localhost:8000/api
┌────────────┴────────────────────────────────────────┐
│  Django 5 (localhost:8000)                          │
│  DRF / simplejwt / cors-headers                      │
│  ┌──────────┐ ┌───────────┐ ┌───────────────┐       │
│  │  users   │ │ resources │ │ recommendations│      │
│  │  app     │ │   app     │ │     app        │       │
│  └──────────┘ └───────────┘ └───────────────┘       │
│  ┌──────────┐ ┌──────────┐                          │
│  │behaviors │ │   ai     │  ← DeepSeek API          │
│  │  app     │ │   app    │                          │
│  └──────────┘ └──────────┘                          │
└────────────┬────────────────────────────────────────┘
             │
      ┌──────┴──────┐
      │   MySQL     │
      └─────────────┘
```

## Database Schema (6 tables)

```sql
-- Django built-in auth_user (id, username, password, email, etc.)

-- 用户画像 (extends auth_user)
users_userprofile:
  id           BIGINT PK
  user_id      FK → auth_user.id (OneToOne)
  nickname     VARCHAR(50)
  avatar       VARCHAR(200) NULL
  major        VARCHAR(100) NULL     -- 专业
  grade        VARCHAR(20) NULL      -- 年级
  interest_tags JSON                 -- ["Python","机器学习"]
  created_at   DATETIME
  updated_at   DATETIME

-- 学习资源
resources_resource:
  id           BIGINT PK
  title        VARCHAR(200)
  description  TEXT
  resource_type VARCHAR(20)  -- video/article/exercise
  category     VARCHAR(100)  -- Python/数据结构/AI...
  tags         JSON          -- ["递归","二叉树"]
  difficulty   VARCHAR(20)   -- beginner/intermediate/advanced
  source       VARCHAR(200)  -- B站/CSDN/LeetCode
  url          VARCHAR(500)  -- 外链
  cover_image  VARCHAR(500) NULL
  avg_rating   FLOAT DEFAULT 0  -- 缓存均值
  rating_count INT DEFAULT 0    -- 缓存计数
  browse_count INT DEFAULT 0
  created_by_id FK → auth_user.id
  created_at   DATETIME
  updated_at   DATETIME

-- 用户行为日志
behaviors_userbehavior:
  id           BIGINT PK
  user_id      FK → auth_user.id
  resource_id  FK → resources_resource.id
  behavior_type VARCHAR(20)  -- browse/bookmark/rate
  rating       TINYINT NULL  -- 1-5, only when rate
  created_at   DATETIME
  UNIQUE(user_id, resource_id, behavior_type) for rate & bookmark

-- 推荐结果缓存
recommendations_userrecommendation:
  id           BIGINT PK
  user_id      FK → auth_user.id
  resource_id  FK → resources_resource.id
  predicted_rating FLOAT
  reason       VARCHAR(500)  -- "与您相似的3位用户也喜欢..."
  is_cold_start BOOL
  created_at   DATETIME
  UNIQUE(user_id, resource_id)

-- 用户相似度矩阵 (预计算)
recommendations_usersimilarity:
  ...

-- AI 对话记录
ai_conversation:
  id           BIGINT PK
  user_id      FK → auth_user.id
  title        VARCHAR(100)          -- 会话标题（首条消息截取）
  messages     JSON                  -- [{role, content, time}]
  created_at   DATETIME
  updated_at   DATETIME
```

## API Endpoints

所有接口前缀 `/api/`，JWT Bearer 认证。

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/register/ | - | 注册 |
| POST | /api/auth/login/ | - | 登录 → {access, refresh, user} |
| POST | /api/auth/refresh/ | - | 刷新 token |
| GET | /api/users/me/ | ✓ | 个人信息 |
| PUT | /api/users/me/ | ✓ | 更新个人信息 |
| PUT | /api/users/me/password/ | ✓ | 修改密码 |
| GET | /api/resources/ | - | 资源列表 (?page=&category=&search=) |
| GET | /api/resources/:id/ | opt | 资源详情 (+ user_rating, is_bookmarked) |
| POST | /api/resources/ | admin | 创建资源 |
| PUT/DELETE | /api/resources/:id/ | admin | 更新/删除资源 |
| POST | /api/behaviors/browse/ | ✓ | 记录浏览 |
| POST | /api/behaviors/bookmark/ | ✓ | 切换收藏 (toggle) |
| POST | /api/behaviors/rate/ | ✓ | 评分 {resource_id, rating: 1-5} |
| GET | /api/users/me/history/ | ✓ | 浏览历史 |
| GET | /api/users/me/favorites/ | ✓ | 收藏列表 |
| GET | /api/users/me/ratings/ | ✓ | 评分列表 |
| GET | /api/recommendations/ | ✓ | 推荐列表 (?refresh=false) |
| POST | /api/recommendations/refresh/ | ✓ | 刷新推荐 |
| GET | /api/ai/conversations/ | ✓ | 会话列表 |
| POST | /api/ai/conversations/ | ✓ | 新建会话 |
| GET | /api/ai/conversations/:id/ | ✓ | 会话消息 |
| POST | /api/ai/chat/ | ✓ | 发送消息 (SSE 流式) |
| DELETE | /api/ai/conversations/:id/ | ✓ | 删除会话 |
| GET | /api/stats/popular/ | - | 热门资源 |
| GET | /api/stats/latest/ | - | 最新资源 |

## Frontend Component Tree

```
App.vue
├── AppHeader.vue              -- Logo + 导航 + 搜索 + 用户菜单
├── <router-view>
│   ├── / → HomePage.vue       -- 推荐列表 + 热门 + 最新
│   ├── /resource/:id → ResourceDetailPage.vue  -- 详情 + 评分 + 收藏
│   ├── /login → LoginPage.vue
│   ├── /register → RegisterPage.vue
│   └── /profile → ProfilePage.vue  -- 需要登录
│       ├── ProfileInfo.vue    -- 编辑资料
│       ├── BrowseHistory.vue  -- 浏览历史
│       ├── FavoritesList.vue  -- 我的收藏
│       ├── RatingsList.vue    -- 我的评分
│       └── PasswordChange.vue
├── AIChatBubble.vue           -- 右下角悬浮气泡按钮
├── AIChatPanel.vue            -- 聊天面板（滑出）
│   ├── ChatMessageList.vue    -- 消息列表
│   ├── ChatInput.vue          -- 输入框 (支持 Enter 发送)
│   └── ConversationList.vue   -- 历史会话列表
└── AppFooter.vue

Pinia Stores:
  stores/auth.js       -- 登录状态、用户信息、token 管理
  stores/resource.js   -- 资源列表、推荐、详情
  stores/behavior.js   -- 历史、收藏、评分
  stores/chat.js        -- AI 对话状态、SSE 流式、会话列表
```

## UserCF Algorithm

文件：`backend/apps/recommendations/engine.py`

**核心流程：**
1. 从 behaviors 表拉取所有评分 → 构建用户-资源矩阵 (numpy 2D array)
2. 用 adjusted cosine similarity 计算目标用户与其他用户的相似度
3. 选出 Top-K (K=20) 最近邻
4. 预测未评分资源的评分：
   `pred(u,i) = avg(u) + Σ[sim(u,v) × (r_vi − avg(v))] / Σ|sim(u,v)|`
5. 取 Top-N (N=20) 高预测分资源作为推荐

**冷启动策略：**
- 新用户（行为数 < 5）：返回热门资源（按 avg_rating × browse_count 排序）
- 新资源（评分 < 2）：基于标签匹配推给相关兴趣用户（content-based boost）

**重算触发：**
- 用户点击"刷新推荐"按钮
- 新增行为数 ≥ 5 时标记 stale，下次 GET 触发重算
- 缓存超过 1 小时自动重算

## Design System — Emerald Code

采用浅色默认 + CSS 变量驱动暗色切换的 Emerald Code 设计体系。

**色彩 Token（Light / Dark 双模）：**

| Token | Light | Dark | 用途 |
|-------|-------|------|------|
| `background` | `#f7f9fb` | `#0b1326` | 页面底色 |
| `surface` | `#f7f9fb` | `#0b1326` | 卡片/面板 |
| `surface-container` | `#eceef0` | `#171f33` | 次级容器 |
| `on-surface` | `#191c1e` | `#dae2fd` | 正文文字 |
| `primary` | `#006c49` | `#4edea3` | 主色（按钮/链接/强调） |
| `primary-container` | `#10b981` | `#10b981` | 主色容器 |
| `outline` | `#6c7a71` | `#86948a` | 边框 |
| `outline-variant` | `#bbcabf` | `#3c4a42` | 浅边框 |

**字体规范：**

| 层级 | 字体 | 大小 | 字重 |
|------|------|------|------|
| Display | Space Grotesk | 48px | 700 |
| H1 | Space Grotesk | 32px | 600 |
| H2 | Space Grotesk | 24px | 600 |
| H3 | Space Grotesk | 18px | 500 |
| Body LG | Inter | 16px | 400 |
| Body MD | Inter | 14px | 400 |
| Code/Label | Space Grotesk | 12px | 400/600 |

**布局与深度：**
- 12 列流式网格 + 8px 基准间距
- 3 层深度：Background → Surface → Raised（1px 边框 + 无阴影 → hover 翡翠绿边框过渡）
- 玻璃面板：`rgba(255,255,255,0.7)` + `backdrop-blur(12px)`
- 暗色模式通过 `[data-theme="dark"]` 选择器覆盖 CSS 变量

**参考实现：**
- Light 基准：`stitch_cs_resource_recommender (1)/code.html`
- Dark Token：`id_mind/stitch_cs_resource_recommender/DESIGN.md`

## AI Assistant (DeepSeek API)

文件：`backend/apps/ai/deepseek_client.py`

**System Prompt 核心要素：**
- 角色：计算机专业学习助手
- 能力：回答 CS 问题、解释推荐理由、给出学习建议
- 上下文注入：用户画像（专业/年级/兴趣标签）、近期学习行为摘要、当前浏览资源信息

**和推荐系统的联动：**
- 用户在资源详情页打开 AI 气泡 → 自动注入当前资源作为上下文
- 用户问"这个为什么推荐给我"→ backend 查 UserCF 推荐结果，注入 top-3 相似用户特征
- 用户问"下一步学什么"→ backend 查行为记录 + 推荐结果，让 AI 综合给出建议

**SSE 流式响应：**
- `POST /api/ai/chat/` 返回 `text/event-stream`
- 前端用 `EventSource` 或 `fetch` + `ReadableStream` 逐字渲染
- 完成后保存完整消息到 `ai_conversation.messages` JSON 字段

## Project Directory

```
e:\claude_code\claudecode_keshe\
├── CLAUDE.md
├── PRD.md
├── IMPLEMENTATION_PLAN.md
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/           -- settings.py, urls.py, wsgi.py
│   └── apps/
│       ├── users/        -- models, views, serializers, urls
│       ├── resources/    -- models, views, serializers, permissions
│       ├── behaviors/    -- models, views, signals
│       ├── recommendations/  -- models, engine.py, cold_start.py, views
│       └── ai/            -- models, views, deepseek_client.py
├── frontend/
│   ├── package.json, vite.config.js
│   └── src/
│       ├── main.js, App.vue
│       ├── router/, stores/, api/
│       ├── views/        -- 5 个页面
│       ├── components/   -- layout/, resource/, recommendation/, profile/, common/
│       └── styles/
└── docs/
    ├── thesis-notes.md
    └── demo-script.md
```

## Implementation Phases

| # | 阶段 | 产出 | 依赖 |
|---|------|------|------|
| 1 | **脚手架** | Django + Vue + MySQL 通，跨域联调 OK | - |
| 2 | **用户管理** | 注册/登录/个人中心，JWT 认证 | 1 |
| 3 | **资源管理** | 资源 CRUD（Admin 后台 + API），前端列表/详情/搜索 | 2 |
| 4 | **行为追踪** | 浏览/收藏/评分 API，前端交互组件，历史/收藏/评分列表 | 3 |
| 5 | **推荐引擎** ★ | UserCF 算法 + 冷启动 + 推荐 API + 重算触发器 | 4 |
| 6 | **AI 助手** | DeepSeek API 对接 + 会话管理 + 悬浮气泡聊天面板 (SSE 流式) | 2 |
| 7 | **前端推荐** | 首页推荐列表、刷新推荐、冷启动提示 | 5 |
| 8 | **种子数据 & 打磨** | 50 用户 + 100 资源 + 500 行为数据、UI 细节、答辩文档 | 7 |

## Key Files (最核心)

| 文件 | 重要性 |
|------|--------|
| `backend/apps/recommendations/engine.py` | UserCF 算法实现，答辩核心 |
| `backend/apps/ai/deepseek_client.py` | DeepSeek API 对接 + System Prompt + 上下文注入 |
| `backend/apps/behaviors/models.py` | 行为日志模型，连接用户和资源 |
| `backend/apps/recommendations/views.py` | 推荐调度：冷启判断 + 算法调用 + 缓存 |
| `frontend/src/components/AIChatPanel.vue` | AI 聊天面板，SSE 流式渲染 |
| `frontend/src/stores/resource.js` | 资源和推荐状态管理 |
| `frontend/src/views/HomePage.vue` | 最复杂页面，推荐/热门/最新整合 |

## Tech Versions

| 组件 | 版本 |
|------|------|
| Python | 3.12 |
| Django | 5.0.x |
| DRF | 3.15.x |
| simplejwt | 5.3.x |
| django-cors-headers | 4.4.x |
| mysqlclient | 2.2.x |
| numpy | 1.26.x |
| Node | 20 LTS |
| Vue | 3.5.x |
| Vite | 5.x |
| Element Plus | 2.8.x |
| Pinia | 2.2.x |
| Axios | 1.7.x |

## Verification

- 每阶段完成后用 Playwright MCP 截图验证页面渲染
- 推荐引擎单元测试：固定数据集验证相似度计算和预测评分
- 种子数据加载后用不同用户登录，验证推荐结果有差异
- 新用户登录确认冷启动返回热门资源
