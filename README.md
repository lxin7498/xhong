# CodePath AI - Computer Science Learning Resource Recommendation System

CodePath AI is a personalized learning resource recommendation platform for computer science students. It combines behavior tracking, collaborative filtering, resource management, and an AI learning assistant to help learners discover what to study next.

## Core Features

- User registration, login, profile, and JWT authentication
- Learning resource browsing, search, filtering, detail pages, and ratings
- Behavior records for browsing, bookmarking, and scoring resources
- Personalized recommendations with cold-start fallback and collaborative filtering
- Vue learning dashboard with resource cards, recommendations, and AI assistant entry
- FastAPI-based AI assistant service prepared for LangChain / LangGraph workflows

## Tech Stack

- Frontend: Vue 3, Vite, Pinia, Vue Router, Element Plus
- Backend API: Django, Django REST Framework, SimpleJWT
- AI service: FastAPI, LangChain ecosystem, SSE streaming
- Database: MySQL
- Recommendation: User behavior matrix, collaborative filtering, cold-start popular resources

## Project Structure

```text
backend/      Django REST API and recommendation modules
frontend/     Vue 3 frontend application
my_agent/     FastAPI AI learning assistant service
docs/         Product docs, architecture notes, screenshots, and E2E snapshots
```

## Local Setup

1. Create a MySQL database named `cs_recsys`.
2. Copy environment templates:

```bash
copy backend\.env.example backend\.env
copy my_agent\.env.example my_agent\.env
copy frontend\.env.example frontend\.env
```

3. Start the Django backend:

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

4. Start the AI service:

```bash
cd my_agent
pip install -r requirements.txt
python -m uvicorn my_agent.main:app --host 0.0.0.0 --port 8100
```

5. Start the frontend:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open `http://127.0.0.1:5173`.

## Verification

```bash
cd backend
python manage.py check
python manage.py test apps.resources.tests apps.recommendations.tests apps.behaviors.tests apps.users.tests

cd frontend
npm run build
```

## Portfolio Highlights

- Recommendation logic is not a static mock: user behavior changes recommendation results.
- The system records browse, bookmark, and rating signals for learner modeling.
- AI assistant is isolated as a service, so it can evolve independently from the main API.
- The project can be demonstrated as a learning dashboard rather than a traditional CRUD admin system.
