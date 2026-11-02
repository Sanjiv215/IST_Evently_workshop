# EventHub &bull; Event Registration Platform

A production-ready event management and registration application built with **Flask**, **PostgreSQL (Supabase)**, and modern responsive frontend.

---

## Features

- **Browse Events**: Real-time listing of available events with capacities and organizer metadata.
- **1-Click Registration**: Register for events with built-in duplicate prevention and capacity validation.
- **My Registrations View**: View all events the active user has signed up for.
- **Organizer Attendee List**: Inspect who has registered for any event.
- **Interactive API Documentation**: Live interactive Swagger-style documentation accessible at `/docs`.
- **Flexible Identity Handling**: Identifies users via `X-User-Id` header, URL query parameter (`?user_id=...`), or request body.
- **Zero-Build Frontend**: Vanilla HTML/CSS/JS frontend served directly by Flask with zero bundle step or external build tools.
- **Pre-commit Security**: Built-in Husky and Gitleaks pre-commit hooks to prevent accidental credential and secret exposure.

---

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.1, Gunicorn (Production WSGI)
- **Database**: PostgreSQL hosted on Supabase (PostgREST API)
- **Frontend**: Responsive modern UI with native Fetch API and CSS variables
- **Security & Quality**: Gitleaks, Husky

---

## API Contract

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/events` | Browse all available events |
| `GET` | `/api/events/<id>` | Fetch specific event details |
| `POST` | `/api/registrations` | Register user for an event (201 Created or 409 Conflict) |
| `GET` | `/api/me/registrations` | View registrations for the active user |
| `GET` | `/api/events/<id>/registrations` | View attendee list for an event |
| `GET` | `/docs` | Interactive API documentation |

---

## Quickstart

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd new1
```

### 2. Set up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-publishable-key
PORT=5001
```

### 4. Database Setup (Supabase)
Run the following SQL in your **Supabase SQL Editor**:
```sql
create extension if not exists "pgcrypto";

create table if not exists public.users (
    id uuid primary key default gen_random_uuid(),
    email text unique not null,
    role text check (role in ('student', 'organizer')) not null default 'student'
);

create table if not exists public.events (
    id uuid primary key default gen_random_uuid(),
    title text not null,
    capacity int not null default 50,
    organiser_id uuid references public.users(id) on delete cascade,
    timestamp timestamptz default now()
);

create table if not exists public.registrations (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users(id) on delete cascade,
    event_id uuid not null references public.events(id) on delete cascade,
    created_at timestamptz default now(),
    constraint unique_user_event unique (user_id, event_id)
);

alter table public.users disable row level security;
alter table public.events disable row level security;
alter table public.registrations disable row level security;
```

### 5. Run Development Server
```bash
python app.py
```
Open **`http://127.0.0.1:5001/`** in your browser.

---

## Production Deployment

### Running with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Deploying to Render / Railway / Fly.io
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
- **Environment Variables**: Add `SUPABASE_URL` and `SUPABASE_KEY` in your hosting dashboard.

---

## Security

This repository uses **Gitleaks** with **Husky** to prevent credentials from ever being committed:
```bash
npm install
```
Commits containing secrets or API tokens will be blocked automatically.
