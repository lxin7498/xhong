# Project Structure

This project has three runnable parts: the Django API, the Vue frontend, and the FastAPI AI assistant.

## Clean Source View

```text
claudecode_keshe/
├─ backend/                 # Django REST API
│  ├─ apps/                 # Business modules
│  │  ├─ users/             # Login, register, profile
│  │  ├─ resources/         # Learning resources
│  │  ├─ behaviors/         # Browse, bookmark, rating records
│  │  ├─ recommendations/   # Collaborative filtering recommendation logic
│  │  └─ ai/                # Legacy AI API placeholder
│  ├─ config/               # Django settings, URLs, pagination
│  ├─ .env.example          # Backend environment template
│  ├─ manage.py
│  ├─ requirements.txt
│  └─ seed_resources.py
├─ frontend/                # Vue 3 application
│  ├─ public/
│  ├─ src/
│  │  ├─ api/               # Axios client
│  │  ├─ components/        # Layout, resource cards, AI panel
│  │  ├─ router/            # Vue Router
│  │  ├─ stores/            # Pinia stores
│  │  ├─ styles/            # Global style tokens
│  │  └─ views/             # Pages
│  ├─ .env.example          # Frontend environment template
│  ├─ package.json
│  └─ vite.config.js
├─ my_agent/                # FastAPI AI learning assistant
│  ├─ .env.example          # Agent environment template
│  ├─ agent.py
│  ├─ env_utils.py
│  ├─ main.py
│  ├─ my_llm.py
│  ├─ tools.py
│  └─ requirements.txt
├─ docs/                    # Product, architecture, screenshots
├─ README.md
├─ .gitignore
├─ AGENTS.md
└─ CLAUDE.md
```

## Local-Only Noise

These files and folders are normal during development, but they should not be treated as project source code:

```text
backend/venv/               # Python virtual environment
frontend/node_modules/      # npm dependencies
frontend/dist/              # frontend build output
my_agent/.env               # local secret config
**/__pycache__/             # Python cache
.claude/ .codex/            # local AI tool state
.playwright-mcp/            # local browser testing state
```

The workspace includes `.vscode/settings.json` to hide these noisy folders in VS Code so the project tree looks closer to the clean source view.
