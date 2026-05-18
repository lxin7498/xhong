# 学堂精英 · CS Academy Elite

面向计算机专业学生的个性化学习资源推荐系统。通过行为追踪、协同过滤与 AI 助手，帮助学习者发现适合自己的下一步学习内容。

## 项目背景

计算机专业学生在自主学习时常面临两个难题：海量资料无从下手，学习路径缺乏个性化引导。本项目尝试用推荐系统 + AI 助手的组合来解决这个痛点——不是简单地做一个资源列表网站，而是让系统真正"了解"每个学习者的兴趣和进度，给出可信的建议。

## 核心功能

- **用户系统** — 注册、登录、个人资料、密码修改，基于 JWT 的身份认证
- **学习资源** — 资源浏览、搜索、分类筛选、详情页、评分
- **行为追踪** — 自动记录浏览、收藏、评分等行为，作为推荐的数据基础
- **个性化推荐** — 协同过滤推荐引擎，支持冷启动兜底策略，推荐结果随用户行为动态变化
- **AI 学习助手** — 流式对话面板，支持多模型切换（智谱 / DeepSeek / 通义），上下文持久化

## 技术栈

| 模块 | 技术选型 |
|------|----------|
| 前端 | Vue 3、Vite、Pinia、Vue Router、Element Plus |
| 后端 API | Django、Django REST Framework、SimpleJWT |
| AI 服务 | FastAPI、LangChain 生态、SSE 流式响应 |
| 数据库 | MySQL |
| 推荐引擎 | 用户行为矩阵、协同过滤、热度兜底 |

> 将 AI 服务独立部署，而非嵌入 Django 内部，使其可以独立演进、独立扩容，不受后端 API 框架约束。

## 项目结构

```
backend/          Django REST API + 推荐引擎 + 行为追踪模块
  apps/
    users/            用户系统
    resources/        学习资源管理
    behaviors/        用户行为记录
    recommendations/  推荐引擎
    ai/               AI 服务网关（预留）
  config/             Django 项目配置
frontend/         Vue 3 前端应用
  src/
    components/       ChatBubble、ChatPanel、ResourceCard 等组件
    views/            首页、登录、注册、个人中心、资源详情、资源列表
    stores/           状态管理（auth、resource、behavior、ai、app）
    router/           路由 + 导航守卫
my_agent/         FastAPI AI 学习助手
docs/             产品文档、架构设计、截图、E2E 测试用例
```

## 本地运行

### 环境准备

需要 Python 3.12+、Node.js 18+、MySQL 8.0+。

在 MySQL 中创建数据库：
```sql
CREATE DATABASE cs_recsys CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 1. 配置环境变量

```bash
# 三个模块各有一份 .env 模板，复制后按需修改
cp backend/.env.example backend/.env
cp my_agent/.env.example my_agent/.env
cp frontend/.env.example frontend/.env
```

在 `backend/.env` 中填写数据库连接信息，在 `my_agent/.env` 中填写大模型 API Key（至少配置一个）。

### 2. 启动 Django 后端

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 3. 启动 AI 助手

```bash
cd my_agent
pip install -r requirements.txt
python -m uvicorn my_agent.main:app --host 0.0.0.0 --port 8100
```

### 4. 启动前端

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

浏览器打开 `http://127.0.0.1:5173` 即可使用。

## 验证测试

```bash
# Django 检查 & 测试
cd backend
python manage.py check
python manage.py test apps.resources.tests apps.recommendations.tests apps.behaviors.tests apps.users.tests

# 前端构建检查
cd frontend
npm run build
```

## 设计亮点

- **推荐不是静态 mock** — 用户行为（浏览、收藏、评分）会实时影响推荐结果，可以实际演示
- **冷启动兜底** — 新用户没有行为数据时，自动回退到热门资源推荐，体验不中断
- **AI 服务独立** — FastAPI + 流式 SSE，与 Django 解耦，可独立调试和扩展
- **仪表盘视角** — 前端设计为"学习仪表盘"而非传统后台管理，更适合演示和毕业答辩

## 许可证

MIT License