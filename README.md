# QUAICU — AI-Mediated Group Decision-Making Platform

A production-ready Turborepo monorepo with a **Python FastAPI** API backend, **Next.js 14** (App Router) frontend, and a **shared TypeScript/Zod** package.

---

## Prerequisites

| Tool       | Version  |
|------------|----------|
| Node.js    | ≥ 18.x   |
| Python     | ≥ 3.11   |
| npm        | ≥ 9.x    |
| Docker     | ≥ 20.x   |
| Docker Compose | ≥ 2.x |

---

## Quick Start

```bash
# 1. Clone the repo
cd quaicu

# 2. Start Postgres + Redis + API
docker-compose up -d

# 3. Install frontend dependencies
npm install

# 4. Initialize Python Backend & Migrations
cd apps/api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
cd ../..

# 5. Start development servers
npm run dev:api
npm run dev:web
```

- **API**:  http://localhost:3001
- **Swagger Docs**:  http://localhost:3001/api/docs
- **Frontend**:  http://localhost:3000

---

## Environment Variables

### `apps/api/.env`

| Variable        | Default                                             | Description              |
|-----------------|------------------------------------------------------|--------------------------|
| `DATABASE_URL`  | `postgresql://postgres:postgres@localhost:5432/quaicu` | PostgreSQL connection    |
| `REDIS_URL`     | `redis://localhost:6379`                              | Redis connection         |
| `JWT_SECRET`    | `changeme_use_strong_secret_in_prod`                  | JWT signing secret       |
| `JWT_EXPIRY`    | `7d`                                                  | JWT token lifetime       |
| `PORT`          | `3001`                                                | API server port          |

### `apps/web/.env.local`

| Variable              | Default                    | Description            |
|-----------------------|----------------------------|------------------------|
| `NEXTAUTH_URL`        | `http://localhost:3000`    | Auth.js callback URL   |
| `NEXTAUTH_SECRET`     | `changeme`                 | Auth.js session secret |
| `NEXT_PUBLIC_API_URL` | `http://localhost:3001`    | API base URL           |

---

## Project Structure

```
quaicu/
├── apps/
│   ├── api/              → NestJS backend
│   │   ├── prisma/       → Prisma schema & migrations
│   │   └── src/
│   │       ├── auth/     → JWT auth, guards, strategies
│   │       ├── decisions/ → Decision CRUD
│   │       ├── participants/ → Invite/remove participants
│   │       ├── prisma/   → PrismaService (global)
│   │       ├── app.module.ts
│   │       └── main.ts
│   └── web/              → Next.js 14 (App Router) frontend
│       └── src/
│           ├── app/
│           │   ├── login/
│           │   ├── register/
│           │   └── dashboard/
│           ├── auth.ts   → Auth.js v5 config
│           └── lib/api.ts → Fetch wrapper with Bearer token
├── packages/
│   └── shared/           → Enums, Zod schemas, TS types
├── docker-compose.yml
├── turbo.json
└── package.json
```

---

## API Routes

All protected routes require `Authorization: Bearer <JWT>` header.

### Authentication (Public)

| Method | Path                      | Description            |
|--------|---------------------------|------------------------|
| POST   | `/api/v1/auth/register`   | Register a new user    |
| POST   | `/api/v1/auth/login`      | Login, returns JWT     |

### Decisions (Protected)

| Method | Path                      | Description                                |
|--------|---------------------------|--------------------------------------------|
| POST   | `/api/v1/decisions`       | Create a new decision                      |
| GET    | `/api/v1/decisions`       | List user's decisions                      |
| GET    | `/api/v1/decisions/:id`   | Get decision details                       |
| PATCH  | `/api/v1/decisions/:id`   | Update decision (owner only, DRAFT only)   |

### Participants (Protected)

| Method | Path                                           | Description                              |
|--------|-------------------------------------------------|------------------------------------------|
| POST   | `/api/v1/decisions/:id/participants`            | Invite participant (owner only)          |
| DELETE | `/api/v1/decisions/:id/participants/:userId`    | Remove participant (owner only)          |

---

## Scripts

| Script         | Description                         |
|----------------|-------------------------------------|
| `npm run dev`  | Start all apps in parallel (Turbo)  |
| `npm run build`| Build all packages/apps             |
| `npm run lint` | Lint all packages/apps              |

---

## Tech Stack

| Layer      | Technology                           |
|------------|--------------------------------------|
| Monorepo   | Turborepo + npm workspaces           |
| Backend    | NestJS 10, Prisma 5, PostgreSQL 15   |
| Auth       | JWT (7d), bcrypt, Passport-JWT       |
| Frontend   | Next.js 14 (App Router), Auth.js v5  |
| Shared     | TypeScript, Zod                      |
| Infra      | Docker Compose (Postgres + Redis)    |

---

## License

Private — All rights reserved.
