# 运行指南

## 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- npm / npx

## 快速启动

### 1. 数据库

确保 MySQL 运行在 `127.0.0.1:3306`，数据库 `cs_recsys` 已创建：

```bash
mysql -u root -p10086 -e "CREATE DATABASE IF NOT EXISTS cs_recsys CHARACTER SET utf8mb4;"
```

### 2. Django 后端 (端口 8000)

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 加载示例数据（可选）
python manage.py loaddata sample_data.json

# 启动
python manage.py runserver 0.0.0.0:8000
```

### 3. AI Agent 服务 (端口 8100)

```bash
cd my_agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (.env 文件)
# DEEPSEEK_API_KEY=xxx
# ZHIPU_API_KEY=xxx
# DJANGO_BASE_URL=http://127.0.0.1:8000
# AGENT_PORT=8100

# 启动
python -m uvicorn my_agent.main:app --host 0.0.0.0 --port 8100
```

### 4. 前端 (端口 5173)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev -- --host 0.0.0.0
```

访问 `http://127.0.0.1:5173` 即可使用。

## 运行测试

```bash
# 后端测试 (44 tests)
cd backend
python manage.py test apps.resources.tests apps.recommendations.tests apps.behaviors.tests apps.users.tests

# 前端构建验证
cd frontend
npm run build
```

## 验证清单

| 检查项 | 方法 |
|--------|------|
| Django API 正常 | `curl http://127.0.0.1:8000/api/resources/?page_size=1` |
| Agent 健康 | `curl http://127.0.0.1:8100/health` → `{"status":"ok"}` |
| 前端页面 | 浏览器访问 `http://127.0.0.1:5173` |
| AI 聊天 | 点击右下角气泡 → 输入消息 → 查看流式回复 |
| 用户注册/登录 | 右上角注册→登录→查看个性化推荐 |

## 项目结构

```
claudecode_keshe/
├── backend/                 # Django REST API
│   ├── config/              # Django 配置 (settings, urls)
│   ├── apps/
│   │   ├── resources/       # 学习资源
│   │   ├── users/           # 用户认证 + 个人资料
│   │   ├── behaviors/       # 用户行为（浏览/收藏/评分）
│   │   ├── recommendations/ # 推荐引擎（协同过滤）
│   │   └── ai/              # [已废弃] 由 my_agent 替代
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── components/ai/   # AI 助手组件
│       ├── stores/          # Pinia 状态管理
│       ├── router/          # 路由配置
│       └── api/             # API 客户端
├── my_agent/                # FastAPI AI Agent
│   ├── main.py              # SSE 端点 + LangGraph
│   ├── agent.py             # ReAct agent 定义
│   ├── tools.py             # Agent 工具函数
│   └── my_llm.py            # LLM 配置
├── docs/                    # 文档 + 截图
│   ├── ARCHITECTURE.md      # 架构文档
│   ├── RUN_GUIDE.md         # 运行指南（本文件）
│   ├── screenshots/         # 页面截图
│   ├── e2e-tests/           # E2E 测试快照
│   └── playwright-snapshots/# 历史 Playwright 快照
└── CLAUDE.md                # 项目开发规范
```

## 环境变量

### backend/.env
```
DB_NAME=cs_recsys
DB_USER=root
DB_PASSWORD=10086
DB_HOST=127.0.0.1
DB_PORT=3306
SECRET_KEY=django-insecure-xxx
```

### my_agent/.env
```
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
ZHIPU_API_KEY=xxx
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
DJANGO_BASE_URL=http://127.0.0.1:8000
AGENT_PORT=8100
```
