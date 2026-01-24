# Course Companion FTE

**A Digital Full-Time Equivalent Educational Tutor for Generative AI Fundamentals**

[![CI/CD](https://github.com/your-org/course-companion-fte/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-org/course-companion-fte/actions)
[![Coverage](https://codecov.io/gh/your-org/course-companion-fte/branch/master/graph/badge.svg)](https://codecov.io/gh/your-org/course-companion-fte)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

Course Companion FTE is an AI-powered educational tutor that delivers a comprehensive Generative AI Fundamentals course through dual frontends:

- **ChatGPT App**: Conversational interface for learning through natural dialogue
- **Web Application**: Visual dashboard with progress tracking and interactive quizzes

### Course Content (6 Chapters)

1. **Introduction to Generative AI** - Core concepts, history, current landscape
2. **Large Language Models (LLMs)** - Transformer architecture, training, tokenization
3. **Prompt Engineering** - Effective prompting patterns, advanced techniques, security
4. **Retrieval-Augmented Generation (RAG)** - Architecture, embeddings, vector databases
5. **Fine-Tuning LLMs** - When to fine-tune, methods (LoRA, QLoRA), evaluation
6. **Building AI Applications** - Agent architecture, production considerations

### Features

- ✅ **Content Delivery** - Access course chapters through conversational interface
- ✅ **Personalized Explanations** - Multi-level concept explanations (beginner/intermediate/advanced)
- ✅ **Interactive Quizzes** - Immediate feedback with deterministic grading
- ✅ **Progress Tracking** - Streaks, milestones, completion status
- ✅ **Freemium Model** - Chapters 1-3 free, 4-6 premium
- 🔄 **Adaptive Learning** (Phase 2) - AI-powered personalized recommendations
- 🔄 **LLM Assessments** (Phase 2) - Deep evaluation of written responses
- 🔄 **Web Dashboard** (Phase 3) - Full-featured visual interface

## Architecture

### Phase 1: Zero-Backend-LLM (Current)

**Constitutional Requirement**: Backend makes ZERO LLM API calls.

```
User → ChatGPT App → Deterministic Backend (FastAPI)
                     ├─ Content APIs (Cloudflare R2)
                     ├─ Quiz APIs (Rule-based grading)
                     ├─ Progress APIs (PostgreSQL)
                     └─ Cache (Redis)
```

**Cost**: <$0.004/user/month

### Phase 2: Hybrid Intelligence (Planned)

```
User → ChatGPT App → Backend → Claude Sonnet 4.5
                     ├─ /api/v1/* (Deterministic - NO LLM)
                     └─ /api/v2/* (Hybrid - Premium LLM features)
```

**Cost**: <$0.50/premium-user/month

### Phase 3: Web Application (Planned)

Full-featured Next.js web app with responsive design (mobile/tablet/desktop).

## Tech Stack

### Backend (Python 3.11+)
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0+ (async)
- **Database**: PostgreSQL 15+ (Neon/Supabase)
- **Cache**: Redis 7+ (Upstash/Redis Cloud)
- **Storage**: Cloudflare R2 (S3-compatible)
- **Testing**: pytest, pytest-asyncio, pytest-cov

### Frontend (TypeScript 5.3+)
- **Framework**: Next.js 14+ (App Router)
- **UI**: React 18+, TailwindCSS 3.4+, shadcn/ui
- **State**: React Query 5.0+, Zustand 4.4+
- **Testing**: Vitest, Playwright, axe-core

### ChatGPT Integration
- **Platform**: OpenAI Apps SDK
- **Agent Skills**: 4 SKILL.md files (concept-explainer, quiz-master, socratic-tutor, progress-motivator)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/your-org/course-companion-fte.git
cd course-companion-fte
```

### 2. Start Infrastructure (PostgreSQL + Redis)

```bash
docker-compose up -d postgres redis
```

### 3. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, JWT_SECRET_KEY

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### 4. Setup Web App (Phase 3)

```bash
cd web-app

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with NEXT_PUBLIC_API_URL

# Start development server
npm run dev
```

Web app will be available at `http://localhost:3000`

## Development

### Running Tests

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=html
```

**Frontend (Phase 3):**
```bash
cd web-app
npm run test -- --coverage
```

### Linting & Type Checking

**Backend:**
```bash
cd backend
ruff check app/
mypy app/
```

**Frontend:**
```bash
cd web-app
npm run lint
npm run type-check
```

## Project Structure

```
course-companion-fte/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # Phase 1 deterministic endpoints
│   │   ├── api/v2/            # Phase 2 hybrid endpoints (planned)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── skills/            # Agent Skills (SKILL.md)
│   │   └── utils/             # Utilities (auth, storage, cache)
│   ├── alembic/               # Database migrations
│   └── tests/                 # Backend tests
├── chatgpt-app/               # ChatGPT App integration
│   ├── manifest.yaml          # OpenAI Apps manifest
│   └── prompts/               # System prompts
├── web-app/                   # Next.js frontend (Phase 3)
│   ├── app/                   # Next.js 14 App Router
│   ├── components/            # React components
│   └── lib/                   # Utilities
├── content/                   # Course content
│   └── chapters/              # JSON files for 6 chapters
├── specs/                     # Planning artifacts
│   └── 001-course-companion-fte/
│       ├── spec.md            # Requirements
│       ├── plan.md            # Technical design
│       └── tasks.md           # Implementation tasks
└── docker-compose.yml         # Local development stack
```

## Constitutional Principles

This project follows strict constitutional gates:

1. **Zero-Backend-LLM First** (Phase 1) - NON-NEGOTIABLE
2. **Cost Efficiency** (<$0.004/user Phase 1, <$0.50/premium-user Phase 2)
3. **Spec-Driven Development** (Spec → Plan → Tasks → Implement)
4. **Hybrid Intelligence Isolation** (v1 deterministic, v2 hybrid)
5. **Educational Excellence** (4 Agent Skills, 99%+ consistency)

See [.specify/memory/constitution.md](.specify/memory/constitution.md) for full details.

## Documentation

- [Specification](specs/001-course-companion-fte/spec.md) - User requirements
- [Implementation Plan](specs/001-course-companion-fte/plan.md) - Technical design
- [Task Breakdown](specs/001-course-companion-fte/tasks.md) - Implementation tasks
- [Constitution](.specify/memory/constitution.md) - Project principles
- [Planning Summary](PLANNING-COMPLETE.md) - Complete overview

## Deployment

### Backend (Fly.io / Railway)

```bash
cd backend
fly launch  # or railway up
```

### Frontend (Vercel)

```bash
cd web-app
vercel --prod
```

### ChatGPT App (OpenAI Platform)

```bash
cd chatgpt-app
openai apps deploy
```

## Cost Analysis

| Phase | Infrastructure | Per-User Cost | Notes |
|-------|---------------|---------------|-------|
| Phase 1 | $15-60/month | $0.002-0.006/user | Zero LLM costs |
| Phase 2 | +$320/month (1K premium) | $0.32/premium-user | Adaptive + Assessments |
| Phase 3 | +$0-20/month | $0-0.002/user | Vercel hosting |

**Total**: ~$50/month for 10K users (99% cost reduction vs human tutors)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/course-companion-fte/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/course-companion-fte/discussions)
- **Email**: support@course-companion.dev

---

**Built with** ❤️ **using the Agent Factory Architecture**

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
