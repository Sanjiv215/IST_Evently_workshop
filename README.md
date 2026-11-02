# EventHub &bull; Production Architecture

A full-stack event registration platform designed for a distributed multi-cloud architecture:
- **Frontend**: Hosted on **Vercel** (Static UI + Secure Serverless API Proxy)
- **Backend API**: Hosted on **Render** (Flask + Gunicorn WSGI + CORS)
- **Database**: Hosted on **Supabase** (PostgreSQL)

---

## Architecture Overview

```
                      ┌──────────────────────┐
                      │    Vercel Frontend   │
                      │  (No backend visible)│
                      └──────────┬───────────┘
                                 │
                 Requests to     │ /api/* (Same domain)
                                 ▼
                      ┌──────────────────────┐
                      │ Vercel API Proxy     │
                      │ (Reads BACKEND_URL)  │
                      └──────────┬───────────┘
                                 │
                     HTTP / CORS │ Headers: X-User-Id
                                 ▼
                      ┌──────────────────────┐
                      │    Render Backend    │
                      │    (Flask / app.py)  │
                      └──────────┬───────────┘
                                 │
                     REST / SSL  │ Supabase Python SDK
                                 ▼
                      ┌──────────────────────┐
                      │  Supabase Database   │
                      │     (PostgreSQL)     │
                      └──────────────────────┘
```

---

## 1. Backend Deployment (Render)

1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** &rarr; **Web Service**.
3. Select your repository: `Sanjiv215/IST_Evently_workshop`.
4. Configure settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
5. In the **Environment Variables** section, add:
   - `SUPABASE_URL` = *(Your Supabase project URL)*
   - `SUPABASE_KEY` = *(Your Supabase publishable/anon key)*
   - `PYTHON_VERSION` = `3.11.9`
6. Click **Deploy Web Service** and copy your Render URL (e.g. `https://eventhub-backend.onrender.com`).

---

## 2. Frontend Deployment (Vercel)

1. Log in to [Vercel Dashboard](https://vercel.com/).
2. Click **Add New...** &rarr; **Project**.
3. Import your repository: `Sanjiv215/IST_Evently_workshop`.
4. Expand **Environment Variables** and add:
   - **Key**: `BACKEND_URL`
   - **Value**: `https://your-backend.onrender.com` *(Replace with your Render URL)*
5. Click **Deploy**.

> **Note**: No backend URL is displayed in the site. The Vercel serverless proxy securely forwards all `/api/*` and `/docs` requests to the Render URL defined in `BACKEND_URL`.

---

## 3. Local Development

### Run Backend
```bash
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Runs at `http://127.0.0.1:5001`.

### Open Frontend
Open `http://127.0.0.1:5001/` in your browser.

---

## API Contract

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck endpoint for Render |
| `GET` | `/api/events` | Browse all events |
| `GET` | `/api/events/<id>` | Event details |
| `POST` | `/api/registrations` | Create registration (receives `X-User-Id` header) |
| `GET` | `/api/me/registrations` | Current user registrations |
| `GET` | `/api/events/<id>/registrations` | Attendee list for an event |
| `GET` | `/docs` | Interactive API documentation |

---

## Security

This repository uses **Gitleaks** with **Husky** to prevent credentials from ever being committed:
```bash
npm install
```
Commits containing secrets or API tokens will be blocked automatically.
