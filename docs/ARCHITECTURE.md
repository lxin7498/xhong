# CS Academy Elite — 系统架构文档

## 项目概述

CS Academy Elite 是一个**个性化学习资源推荐系统**，面向计算机专业学生提供智能学习资源发现与推荐服务。系统采用协同过滤算法，结合用户行为数据（浏览、收藏、评分）生成个性化推荐，并集成 AI 学习助手提供自然语言交互式资源推荐。

## 技术栈

| 层级 | 技术选型 | 选型理由 |
|------|---------|---------|
| 前端 | Vue 3 + Vite + Pinia | 轻量级响应式框架，开发体验优秀 |
| 后端 API | Django + Django REST Framework | 成熟的 REST API 框架，ORM 和认证体系完善 |
| AI Agent | FastAPI + LangGraph + SSE | 异步流式响应，ReAct agent 架构 |
| LLM | 智谱 GLM-5.1 | 性价比高，中文能力强 |
| 数据库 | MySQL | 关系型数据，支持复杂聚合查询 |
| 缓存 | Django Cache (Redis/LocMem) | 推荐结果缓存，减少重复计算 |

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                    │
│  ┌─────────┐ ┌────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ HomePage │ │Resources│ │  Login/   │ │ AI ChatPanel │  │
│  │          │ │  List   │ │ Register  │ │ + ChatBubble │  │
│  └─────────┘ └────────┘ └──────────┘ └──────────────┘  │
│        │           │           │              │          │
│        ▼           ▼           ▼              ▼          │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Pinia Stores (状态管理)               │   │
│  │  auth.js │ resource.js │ behavior.js │ ai.js     │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / SSE
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ Django (8000)│ │  FastAPI  │ │  DeepSeek    │
│  REST API    │ │ Agent    │ │  / Zhipu     │
│  + DRF       │ │ (8100)   │ │  API         │
│  + JWT       │ │          │ │              │
└──────┬───────┘ └────┬─────┘ └──────────────┘
       │              │
       ▼              ▼
┌──────────────────────────┐
│       MySQL Database     │
│   resources / behaviors  │
│   users / conversations  │
└──────────────────────────┘
```

### 三层架构详解

**1. Django REST API (端口 8000)**
- `apps/resources/` — 学习资源 CRUD，支持搜索、分类筛选、排序
- `apps/users/` — 用户注册/登录 (JWT)，个人资料管理
- `apps/behaviors/` — 用户行为记录（浏览、收藏、评分），评分触发重新计算统计
- `apps/recommendations/` — 协同过滤推荐引擎

**2. FastAPI Agent (端口 8100)**
- 独立于 Django 运行，通过 HTTP 调用 Django API 获取资源数据
- 使用 LangGraph ReAct agent 架构，按需决策调用工具
- SSE (Server-Sent Events) 流式返回 AI 生成内容
- 每类工具限制调用 1 次，防止无限循环

**3. Vue 3 Frontend (端口 5173)**
- 6 个页面：首页、资源广场、资源详情、登录、注册、个人中心
- AI 聊天面板：右侧滑出，SSE 流式渲染，对话历史管理
- 绿色 (Emerald) 主题，Glass morphism 设计风格
- localStorage 持久化对话数据

## 推荐引擎

### 协同过滤算法

基于用户的协同过滤 (User-Based CF)，核心流程：

1. **构建评分矩阵**: 从 UserBehavior 表提取所有评分行为，构建 user × resource 矩阵
2. **计算用户相似度**: 使用调整余弦相似度（均值中心化 + L2 归一化）
3. **预测评分**: 选取 K=20 最近邻用户，加权平均预测未评分资源
4. **冷启动处理**: 新用户（行为 < 5 条）返回热门推荐

### 缓存策略

- 推荐结果缓存 3600 秒 (1小时)
- 新行为触发 `refresh_recommendations()` 使缓存失效
- 用户行为触发评分统计重新计算 (`avg_rating`, `rating_count`)

## AI 助手

### Agent 架构

```
用户消息 → ChatPanel.vue → POST /chat/stream (SSE)
  → LangGraph ReAct Agent
    → get_user_profile() → Django API
    → get_user_behaviors() → Django API
    → search_resources(query) → Django API
    → get_resource_detail(id) → Django API
  → 组装 system prompt (含用户画像、行为、匹配资源)
  → Zhipu GLM-5.1 stream → SSE chunks
  → ChatPanel 实时渲染
```

### System Prompt 设计

核心策略：将用户画像、近期行为、匹配资源库注入 system prompt，LLM 据此生成个性化推荐回复。无匹配资源时诚实告知并给出学习路径建议。

### 对话管理

- 前端 localStorage 持久化 conversations 和 messages
- 自动生成对话标题（取首条用户消息前30字）
- 流式响应中禁用输入，防止重复提交

## 数据模型

### resources.Resource
```
title, description, resource_type(video/article/exercise),
category, tags[], difficulty(beginner/intermediate/advanced),
source, url, cover_image,
avg_rating(缓存), rating_count(缓存), browse_count(缓存)
```

### behaviors.UserBehavior
```
user(FK), resource(FK),
behavior_type(browse/bookmark/rate),
rating(nullable), created_at
```

### users.UserProfile
```
user(OneToOne), nickname, avatar,
major, grade, interest_tags[]
```
(由 post_save signal 自动创建)

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /api/resources/ | 资源列表/创建(仅admin) |
| GET/PUT/DEL | /api/resources/{id}/ | 资源详情/更新/删除 |
| POST | /api/auth/register/ | 用户注册 |
| POST | /api/auth/login/ | JWT 登录 |
| GET/PUT | /api/users/me/ | 个人资料 |
| POST | /api/behaviors/browse/ | 记录浏览 |
| POST | /api/behaviors/bookmark/ | 收藏/取消 |
| POST | /api/behaviors/rate/ | 评分 |
| GET | /api/behaviors/history/ | 浏览历史 |
| GET | /api/behaviors/favorites/ | 收藏列表 |
| GET | /api/behaviors/ratings/ | 评分列表 |
| GET | /api/recommendations/ | 个性化推荐 |
| POST | /chat/stream | AI 聊天 (Agent 8100端口) |
